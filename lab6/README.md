# Lab 6 - Inside the xv6 File System

This directory contains the xv6 user programs required by Lab 6.

- `mystat.c` prints the type, inode number, link count, and size of every path supplied on the command line.
- `find.c` recursively prints paths whose last path component matches the requested name.

Copy both files into `~/xv6-riscv/user/` and add `$U/_mystat\` and `$U/_find\` to `UPROGS` in the xv6 `Makefile` before building.
