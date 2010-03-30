#!/usr/bin/env python
#
import sys

lines = sys.stdin.readlines()

# Skip first line
lines = lines[1:]
# continue output while first char is a '#'
for line in lines:
	if line[0] != '#':
		break
	line = line[1:]
	while line[0] == ' ':
		line = line[1:]
	sys.stdout.write(line)
