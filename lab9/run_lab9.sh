#!/bin/sh
# Runs every command of Lab 9 and saves the output in strace-output.txt.
# Needs strace (CachyOS: paru -S strace).
cd "$(dirname "$0")" || exit 1
OUT=strace-output.txt
{
echo "### Part 1: strace -f -e trace=openat,read,write,close ls -l"
strace -f -e trace=openat,read,write,close ls -l 2>&1
echo
echo "### Part 1: number of system calls made by ls -l"
strace -f ls -l 2>&1 >/dev/null | grep -c '^[a-z_0-9]*('
echo
echo "### Part 2: gcc -Wall -Wextra -o syscalls syscalls.c && ./syscalls"
gcc -Wall -Wextra -o syscalls syscalls.c && ./syscalls
echo
echo "### Part 2: strace -e trace=openat,write,read,close ./syscalls"
strace -e trace=openat,write,read,close ./syscalls 2>&1
echo
echo "### Part 3: strace -c ./syscalls"
strace -c ./syscalls 2>&1 >/dev/null
echo
echo "### Part 3: strace -c ls -l"
strace -c ls -l 2>&1 >/dev/null
echo
echo "### Part 3: calls to write made by ls -l"
strace -f -e trace=write ls -l 2>&1 >/dev/null | grep -c '^write('
} > "$OUT"
cat "$OUT"
