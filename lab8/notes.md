# Lab 8 - The Same Calls, Inside Your Own OS: answers to the "Observe" boxes

## Part 1 - run, inside xv6
1. xv6: `fork`, `exec`, `wait`. Linux (Lab 7): `fork`, `execlp`, `waitpid`. They are the same three steps: `fork` copies the process, `exec` replaces the child's program, `wait` collects the child's exit status. `execlp` and `waitpid` are libc wrappers/variants of the same kernel operations (`exec` takes the program and its argument list directly, and `wait(&status)` waits for any child). Only the library around them differs.
2. `echo` prints it. After a successful `exec` the child's code is replaced by `echo`, so the text comes from `echo`'s code; `run` only printed the `pid` lines.
3. Because of the argument given to `exit` after the failed `exec`: xv6's `run.c` calls `exit(1)`, while the Linux `run.c` calls `exit(127)`. Both programs print the value the child passed to `exit` (xv6's `wait` returns it as is; on Linux `WEXITSTATUS` extracts it). 127 is the shell convention for "command not found"; 1 is just a generic failure.

## Part 2 - pingpong
1. A pipe is one-directional. With a single pipe both processes would hold the read and the write end, and the parent could read back the byte it had just written before the child ever received it (or the child would get its own pong). Two pipes give each direction its own channel: `p2c` parent to child, `c2p` child to parent.
2. `read(c2p[0], &b, 1)` in the parent. A read on an empty pipe blocks until the child writes the pong, so the parent cannot print "received pong" before the child has answered. The final `wait(0)` then collects the child.
