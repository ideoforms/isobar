#!/usr/bin/python

#------------------------------------------------------------------------
# Generate isobar README from template and current class docstrings
#------------------------------------------------------------------------

import re
import os
import glob

example_files = list(sorted(glob.glob("examples/*ex-*.py")))

v_examples = ""
for example in example_files:
	example = os.path.basename(example)
	v_examples += "* [%s](examples/%s)\n" % (example, example)

files = [ "core", "scalar", "sequence", "chance", "tonal", "static", "fade", "markov", "lsystem", "warp" ]
regexp = '^\s+""" ?(P\w+): (.+?)(\s*"""\s*)?$'
fmt = "    %-20s - %s\n"

v_classes = ""
for prefix in files:
	contents = file("isobar/pattern/%s.py" % prefix, "r").readlines()
	v_classes += "    %s (%s.py)\n" % (prefix.upper(), prefix)
	for line in contents:
		line = line.rstrip()
		
		match = re.search(regexp, line)
		if match:
			classname = match.group(1)
			docs = match.group(2)
			v_classes += fmt % (classname, docs)
	v_classes += "\n"

print(v_examples)
print(v_classes)
