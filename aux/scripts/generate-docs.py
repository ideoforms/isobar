#!/usr/bin/env python3

#------------------------------------------------------------------------
# Generate isobar README from template and current class docstrings
#------------------------------------------------------------------------

import re
import os
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--markdown", action="store_true")
args = parser.parse_args()

example_files = list(sorted(glob.glob("examples/*ex-*.py")))

v_examples = ""
for example in example_files:
	example = os.path.basename(example)
	v_examples += "* [%s](examples/%s)\n" % (example, example)

if not args.markdown:
	print(v_examples)

files = [ "core", "scalar", "sequence", "chance", "tonal", "static", "fade", "markov", "lsystem", "warp" ]
regexp = '^\s+""" ?(P\w+): (.+?)(\s*"""\s*)?$'
fmt = "    %-20s - %s\n"

for prefix in files:
	contents = open("isobar/pattern/%s.py" % prefix, "r").readlines()
	if args.markdown:
		print("## %s" % prefix.title())
		print("View source: [%s.py](https://github.com/ideoforms/isobar/tree/master/isobar/pattern/%s.py)" % (prefix, prefix))
		print()
		print("| Class | Function |")
		print("|-|-|")
	else:
		print("    %s (%s.py)" % (prefix.upper(), prefix))
	for line in contents:
		line = line.rstrip()
		
		match = re.search(regexp, line)
		if match:
			classname = match.group(1)
			docs = match.group(2)

			if args.markdown:
				print("| %s | %s |" % (classname, docs))
			else:
				print(fmt % (classname, docs), end="")
	print()

