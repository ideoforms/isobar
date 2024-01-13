#!/usr/bin/env python3

import re
import isobar_ext

def main():
	classes = vars(isobar)
	class_names = classes.keys()
	pattern_class_names = sorted(filter(lambda name: re.match("^P[A-Z]", name), class_names))
	for class_name in pattern_class_names:
		try:
			cls = classes[class_name]
			abbreviation = cls.abbreviation
		except AttributeError:
			abbreviation = class_name.lower()
		print(f"from ..pattern import {class_name} as {abbreviation}")

if __name__ == "__main__":
	main()
