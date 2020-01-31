#!/usr/bin/env python3

"""Main."""

import sys
from cpu import CPU

# If no filename given, print usage and exit
if len(sys.argv) != 2:
    print("Usage: ls8.py <filename>.ls8")
    sys.exit(0)

# Storage for the program to be loaded
program = []

# Open the file
with open(sys.argv[1]) as f:
    # Read each line
    for line in f:
        # Strip comments and newlines
        line = line[:line.find('#')].lstrip().rstrip()
        # Add line to program
        if len(line) == 8:
            program.append(int(line, 2))

cpu = CPU()
cpu.load(program)
cpu.run()
