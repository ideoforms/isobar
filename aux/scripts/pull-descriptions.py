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
        contents += "## %s\n" % file_dict["name"].title()
        contents += "View source: [%s.py](https://github.com/ideoforms/isobar/tree/master/isobar/pattern/%s.py)\n" % (file_dict["name"], file_dict["name"])
        contents += "| Class | Function |\n"
        contents += "|-|-|\n"
        for class_dict in file_dict["classes"]:
            contents += "| [%s](%s/%s.md) | %s |\n" % (class_dict["classname"],
                                               file_dict["name"],
                                               class_dict["classname"].lower(),
                                               class_dict["short_description"])
        contents += "|-|-|\n"
    print(contents)

def parse_class_data(args):
    # Get all pattern files, excluding __init__'s
    pattern_files = list(sorted(glob.glob("isobar/pattern/[!_]*.py", recursive=True)))

    allDicts = []

    for fname in pattern_files:
        basename = os.path.basename(fname)
        if args.generate_markdown:
            # Check if folder exists
            if not os.path.exists("docs/patterns/%s" % basename[:-3].title()):
                # Make the folder if not
                os.mkdir("docs/patterns/%s" % basename[:-3].title())
        else:
            print("    %s (%s)" % (basename[:-3].title(), basename))

        # Make a new dict for this file
        fileDict = {
            "name" : basename[:-3],
            "classes" : []
        }

        contents = open(fname, "r").read()

        classregex = 'class\s[\w():\s]+"""((?!""").)*"""'
        cmatch = re.search(classregex, contents, re.S)

        # Loop through for each class in the file
        while cmatch != None:
            name = re.search('(?<=class\s)[^(:]+', cmatch.group(), re.S).group()
            desc = re.search('(?<=""")((?!""").)*', cmatch.group(), re.S).group().strip()
            # Format whitespace for easier output
            # Get first line for short description
            desc = desc.split("\n",1)
            shortdesc = desc[0]
            # Get the rest before code for a long description (if available)
            longdesc = None
            output = None
            if (len(desc) > 1):
                desc = desc[1]
                desc = desc.split(">>>",1)
                longdesc = desc[0].strip()
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

            # Gather all information into dict
            classDict = {
                "classname" : name,
                "short_description" : shortdesc,
                "long_description" : longdesc,
                "example_output" : output,
                "arguments" : arguments
            }
            fileDict["classes"].append(classDict)

            # Crop this section out, look for a new match
            cmatch = re.search(classregex, contents, re.S)

        # Append file dict to full dict list
        allDicts.append(fileDict)

    # Return dict list
    return allDicts

if __name__ == "__main__":
    # Look for arguments to output as markdown
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-markdown", action="store_true", help="Generate and write markdown files per pattern")
    parser.add_argument("--generate-readme", action="store_true", help="Generate and output text for README")
    args = parser.parse_args()

    main(args)