# Lab 9 - Watching System Calls with strace

Machine: CachyOS (Arch Linux), `strace` installed with `paru -S strace`.
All raw outputs are in `strace-output.txt` (produced by `run_lab9.sh`).

## Part 1 - See the calls of a real command

Command: `strace -f -e trace=openat,read,write,close ls -l`

Excerpt (the `write` that prints the listing):

```
openat(AT_FDCWD, "/etc/localtime", O_RDONLY|O_CLOEXEC) = 3
read(3, "TZif2\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\20\0\0\0\20\0\0\0\0"..., 4096) = 2424
close(3)                                = 0
write(1, "total 20\n-rw-r--r-- 1 moiseid mo"..., 305) = 305
close(1)                                = 0
close(2)                                = 0
+++ exited with 0 +++
```

Number of system calls made by one `ls -l` (`strace -f ls -l 2>&1 >/dev/null | grep -c '^[a-z_0-9]*('`): **270** (`strace -c` reports 271 in total on another run). Most are start-up calls: `execve`, `mmap`, `mprotect`, `brk`, `openat`/`read`/`close` of the shared libraries, and name-service lookups (`/etc/passwd`, `/etc/group`) to print the owner names. The real work is a single `write` at the end.

**Observe: which system call does `ls` use to print to the screen? To which descriptor does it write?**
`ls` uses the system call `write`, and it writes to descriptor **1** (standard output), which is the terminal: `write(1, "total ...", N)`. The listing itself comes out in one or a few `write` calls after the `openat`/`read`s of the directory have finished.

## Part 2 - A program that calls the kernel directly

Program: `syscalls.c` (open, write, read, close). Build and run:

```
$ gcc -Wall -Wextra -o syscalls syscalls.c
$ ./syscalls
open returned descriptor 3
write sent 14 bytes
read got 14 bytes: hello, kernel
```

Under strace (`strace -e trace=openat,write,read,close ./syscalls`), the lines of the program are:

```
openat(AT_FDCWD, "note.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 3
write(3, "hello, kernel\n", 14)         = 14
close(3)                                = 0
openat(AT_FDCWD, "note.txt", O_RDONLY)  = 3
read(3, "hello, kernel\n", 63)          = 14
close(3)                                = 0
```

The C functions `open`, `write`, `read` and `close` appear one-to-one as the system calls `openat` (glibc's `open` calls `openat` with `AT_FDCWD`), `write`, `read` and `close`. The three `printf` lines are not separate system calls here: stdout is a file/pipe, so libc buffers them and sends them in one `write(1, "open returned descriptor 3\nwrite"..., 80)` at exit (80 bytes), visible at the end of the trace.

**Observe: the descriptor returned by the first `openat` is 3, not 0, 1 or 2. Why are those three already taken?**
Every process starts with three open descriptors inherited from the shell: **0** is standard input (the keyboard), **1** is standard output (the screen) and **2** is standard error (the screen). The kernel always gives the *smallest free* number, so the first file the program opens gets 3. After `close(3)` the number is free again, which is why the second `openat` also returns 3.

## Part 3 - Count one kind of call

The handout lists this part ("Count one kind of call") but contains no instructions for it, so I used the standard tool for counting: `strace -c`, which prints a table of how many times each system call was made.

```
$ strace -c ./syscalls
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
  0.00    0.000000           0         2           read
  0.00    0.000000           0         2           write
  0.00    0.000000           0         4           close
  0.00    0.000000           0         4           openat
  0.00    0.000000           0         8           mmap
  0.00    0.000000           0         1           execve
  ... (brk, mprotect, fstat, newfstatat, getrandom, etc.)
------ ----------- ----------- --------- --------- ----------------
100.00    0.000000           0        41         2 total

$ strace -f -e trace=write ls -l 2>&1 >/dev/null | grep -c '^write('
1
```

Result: `syscalls` makes 41 system calls in total (2 of them fail: `access` and `ioctl`, both normal start-up probes). Its own work is 2 `write` (14 bytes into `note.txt`, and one 80-byte `write` with the three `printf` lines), 4 `openat` (2 libraries + 2 times `note.txt`), 2 `read` (1 library header + the 14 bytes of `note.txt`) and 4 `close`. All the other rows (`mmap`, `brk`, `execve`, ...) are start-up work of the dynamic loader and libc. `ls -l` makes 271 calls but only **1 `write`**: the whole listing is printed in a single call of 305 bytes.
