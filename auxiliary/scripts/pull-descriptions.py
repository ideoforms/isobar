#!/usr/bin/env python3

#------------------------------------------------------------------------
# Pull Pattern subclass descriptions from their pycode formatting
#------------------------------------------------------------------------

import re
import os
import glob
import argparse

def main(args):
    class_data = parse_class_data(args)
    if args.generate_markdown:
        generate_index(class_data)
        generate_class_pages(class_data)
    else:
        for file_dict in class_data:
            print(file_dict["name"])
            for class_dict in file_dict["classes"]:
                print(class_dict)
            print()


def generate_index(class_data):
    """
    Iterates over each of the source files indexed in `class_data`, and outputs
    a single page of Markdown which is the documentation index.
    """
    contents = ""
    for file_dict in class_data:
        contents += "## [%s](%s/%s)\n" % (file_dict["name"].title(),
                                          file_dict["name"],
                                          "index.md")
        contents += "View source: [%s.py](https://github.com/ideoforms/isobar/tree/master/isobar/pattern/%s.py)\n\n" % (
            file_dict["name"], file_dict["name"])
        contents += "| Class | Function |\n"
        contents += "|-|-|\n"
        for class_dict in file_dict["classes"]:
            contents += "| [%s](%s/%s.md) | %s |\n" % (class_dict["classname"],
                                                       file_dict["name"],
                                                       class_dict["classname"].lower(),
                                                       class_dict["short_description"])
        contents += "\n\n"
    # Output to library.md
    with open("docs/patterns/library.md", "w") as f:
        f.write(contents)

def generate_class_pages(class_data):
    # Set the root directory
    root_dir = "docs/patterns"
    for file_dict in class_data:
        # Check if folder exists
        if not os.path.exists(os.path.join(root_dir, file_dict['name'].lower())):
            # Make the folder if not
            os.mkdir(os.path.join(root_dir, file_dict['name'].lower()))
        # Start storing index file data
        index_content = ["# %s\n" % file_dict["name"].title()]
        for class_dict in file_dict['classes']:
            # Format the file text into a list per line
            class_content = []
            class_content.append("# Pattern: %s" % class_dict['classname'])
            class_content.append(class_dict['short_description'])
            if (class_dict['long_description']):
                class_content.append(class_dict['long_description'])
            if (class_dict['arguments']):
                class_content.append("## Arguments")
                class_content.append(class_dict['arguments'])
            if (class_dict['example_output']):
                class_content.append("## Example Output")
                class_content.append("```py\n%s```" % class_dict['example_output'])
            # Output to the proper file (adding .md to the actual file name)
            fname = (os.path.join(root_dir, file_dict['name'].lower(), class_dict['classname'].lower() + ".md"))
            with open(fname, "w") as f:
                f.write("\n\n".join(class_content))
            # Add class data to index file
            index_content.append("- [%s](%s.md): %s" % (class_dict["classname"],
                                                        class_dict["classname"].lower(),
                                                        class_dict["short_description"]))
        # Write the index file contents for this .py file
        fname = (os.path.join(root_dir, file_dict['name'].lower(), "index.md"))
        with open(fname, "w") as f:
            f.write("\n".join(index_content))

def parse_class_data(args):
    # Get all pattern files, excluding __init__'s
    pattern_files = list(sorted(glob.glob("isobar/pattern/[!_]*.py", recursive=True)))

    all_dicts = []

    for fname in pattern_files:
        base_name = os.path.basename(fname)

        # Make a new dict for this file
        file_dict = {
            "name": os.path.splitext(base_name)[0],
            "classes": []
        }

        with open(fname, "r") as f:
            contents = f.read()

        class_regex = 'class\s[\w():\s]+"""((?!""").)*"""'
        cmatch = re.search(class_regex, contents, re.S)

        # Loop through for each class in the file
        while cmatch != None:
            name = re.search('(?<=class\s)[^(:]+', cmatch.group(), re.S).group()
            desc = re.search('(?<=""")((?!""").)*', cmatch.group(), re.S).group().strip()
            # Format whitespace for easier output
            # Get first line for short description
            desc = desc.split("\n", 1)
            short_desc = desc[0]
            # Get the rest before code for a long description (if available)
            long_desc = None
            output = None
            if (len(desc) > 1):
                desc = desc[1]
                desc = desc.split(">>>", 1)
                long_desc = re.sub("\n\s+", "\n", desc[0].strip())
                # See if there is output to fetch from
                if (len(desc) > 1):
                    output = (">>>%s\n" % desc[1])
                    # Remove spaces
                    output = re.sub("\n\s+", "\n", output)

            # Strip out class
            contents = contents[cmatch.end():]

            # Crop this section out, look for the init statement
            arguments = None
            cmatch = re.search('^\s*def __init__\(.+?\):', contents, re.S)
            if (cmatch):
                # Move to this index and search again for arg comments
                contents = contents[cmatch.end():]
                cmatch = re.search('^\s*""".+?"""', contents, re.S)
                if (cmatch):
                    # Arg comments found, format
                    arguments = re.search('(?<=""")((?!""").)*', cmatch.group(), re.S).group().strip()
                    # Remove the first line stating it is the argument
                    arguments = arguments.split("\n")[1:]
                    i = 0
                    for l in arguments:
                        # Format a code block around the name of the arg
                        l = "`%s" % l.strip()
                        l = re.sub(":", "`:", l, 1)
                        arguments[i] = l
                        i += 1
                    arguments = "\n\n".join(arguments)

            # Gather all information into dict
            class_dict = {
                "classname": name,
                "short_description": short_desc,
                "long_description": long_desc,
                "example_output": output,
                "arguments": arguments
            }
            file_dict["classes"].append(class_dict)

            # Crop this section out, look for a new match
            cmatch = re.search(class_regex, contents, re.S)

        # Append file dict to full dict list
        all_dicts.append(file_dict)

    # Return dict list
    return all_dicts

if __name__ == "__main__":
    # Look for arguments to output as markdown
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-markdown", action="store_true",
                        help="Generate and write markdown files per pattern")
    parser.add_argument("--generate-readme", action="store_true", help="Generate and output text for README")
    args = parser.parse_args()

    main(args)