#!/usr/bin/env python3

#------------------------------------------------------------------------
# Pull Pattern subclass descriptions from their pycode formatting
#------------------------------------------------------------------------

import re
import os
import glob
import argparse

# Look for arguments to output as markdown
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--markdown", action="store_true")
args = parser.parse_args()

# Get all pattern files, excluding __init__'s
pattern_files = list(sorted(glob.glob("isobar/pattern/[!_]*.py", recursive=True)))

for fname in pattern_files:
    # Output file name (DEPRICATED, done by generate-docs)
    basename = os.path.basename(fname)
    #if args.markdown:
    #    print("## %s" % basename[:-3].title())
    #    print("View source: [%s](https://github.com/ideoforms/isobar/tree/master/isobar/pattern/%s)\n" % (basename, basename))
    #else:
    #    print("    %s (%s)" % (basename[:-3].title(), basename))

    contents = open(fname, "r").read()

    classregex = 'class\s[\w():]+\s+"""((?!""").)*"""'
    cmatch = re.search(classregex, contents, re.S)

    # Loop through for each class in the file
    while cmatch != None:
        name = re.search('(?<=class\s)[^(:]+', cmatch.group(), re.S).group()
        desc = re.search('(?<=""")((?!""").)*', cmatch.group(), re.S).group()
        # Format whitespace for easier output
        desc = re.sub("\n[^\S\r\n]+", " ", desc)
        desc = re.sub("\n\s","\n", desc).strip()

        if args.markdown:
            # Gather all information
            mdContent = []
            mdContent.append("## %s\n" % name)
            mdContent.append(desc)
            # Output to a file
            newfile = open("zzz/%s.md" % (name), "w")
            newfile.write("\n".join(mdContent))
            newfile.close()
        else:
            print(name)
            print(desc)
            print()
        # Crop this section out, look for a new match
        contents = contents[cmatch.end():]
        cmatch = re.search(classregex, contents, re.S)

    # Class seperator
    if not args.markdown:
        print("---\n")
