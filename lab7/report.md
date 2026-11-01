# Lab 7 - Three Small Programs: answers to the "Observe" boxes

## Part 1 - fork + exec + wait
1. `perror("exec")` comes right after `execlp`. When `execlp` succeeds, the child's code and data are replaced by the new program, so the next line never runs. `execlp` returns only when it fails, which happens with `nosuchprog` because no such file exists in `PATH`. Only then does `perror` print `exec: No such file or directory`.
2. The child prints the parent's PID, which is the PID the parent printed on its first line (`getppid()` in the child equals `getpid()` in the parent).
3. With `ls` the parent sees status 0 (success). With `nosuchprog` it sees 127, the value the child passed to `exit(127)` after the failed exec.

## Part 2 - A zombie, on purpose
1. `ls` has `Z` in the STAT column, shown as `[ls] <defunct>`. It means zombie: the child has terminated, but its parent has not yet called `wait`, so the kernel keeps its process-table entry and exit status.
2. After 20 s the line is gone. `waitpid(pid, &status, 0)` in `zombie.c` collects the exit status, the kernel frees the entry, and the parent then exits.

## Part 3 - Redirection
1. `open` returned 1. POSIX gives a new descriptor the smallest free number. The child had just run `close(1)`, so 0 (stdin) and 2 (stderr) were taken and 1 was the lowest free one.
2. `ls` was not changed and still writes to descriptor 1. But descriptor 1 now refers to `out.txt`, and `exec` keeps open descriptors, so the listing goes into the file instead of the terminal.
3. Descriptor 2 (stderr): `close(2)`, then `open(...)`.

## Part 4 - A pipe
1. Yes, both commands print the same number.
2. `wc` never ends. `ls` finishes normally, and the parent reaps it with its first `wait`.
3. `wc` waits for end-of-file on the pipe, and EOF only arrives when all copies of the write end are closed. The parent still holds `p[1]` open, so `read` keeps blocking.
