# Lab 10 - Add Your Own System Call: trace (xv6)

I added a new system call, `trace` (number 23), to my xv6 tree (`~/xv6-riscv`). A process
that calls `trace(mask)` makes the kernel print every system call whose bit is on in the mask,
with its pid, name and return value. The mask is copied to children by `fork` and kept across
`exec`, so `trace mask command` traces the whole command.

The changes are committed in the xv6 tree as
`45ad329 Lab 10: add the trace system call (SYS_trace = 23)`.
The same diff is saved here in `trace.patch`, and the full QEMU output in `trace-output.txt`.

## Part 1 - The number and the user side

| File | Change |
|------|--------|
| `kernel/syscall.h` | `#define SYS_trace  23` (22 is already `sync` in our tree) |
| `user/user.h` | `int trace(int);` |
| `user/usys.pl` | `entry("trace");` generates the stub `li a7, SYS_trace; ecall; ret` in `user/usys.S` |
| `user/trace.c` | sets the mask on itself, then `exec`s the command (see `trace.c`) |
| `Makefile` | `$U/_trace\` in `UPROGS`, after `$U/_zombie\` |

**Check 1.** Before the kernel side existed, the number already reached the kernel, which
rejected it:

```
$ trace 32 grep hello README
3 trace: unknown sys call 23
trace: failed
```

## Part 2 - The kernel side

| File | Change |
|------|--------|
| `kernel/proc.h` | `int trace_mask;` in `struct proc`, after `name` |
| `kernel/sysproc.c` | `sys_trace()`: reads argument 0 with `argint` and stores it in `myproc()->trace_mask` |
| `kernel/syscall.c` | `extern uint64 sys_trace(void);`, `[SYS_trace] = sys_trace` in the table, the `syscallnames[]` table above `syscall()`, and the print after the call |
| `kernel/proc.c` | `np->trace_mask = p->trace_mask;` in `fork()` |

The print in `syscall()` comes **after** the call, so the return value is already in `a0`
(the kernel prints with `printk`, not `printf`, in our tree):

```c
    p->trapframe->a0 = syscalls[num]();
    if((p->trace_mask >> num) & 1)
      printk("%d: syscall %s -> %ld\n",
             p->pid, syscallnames[num], p->trapframe->a0);
```

**Check 2.** The numbers are exactly the expected ones: 1023 + 965 + 453 = 2441 bytes, the size
of `README`, read in three pieces, then 0 at the end of the file.

```
$ trace 32 grep hello README
3: syscall read -> 1023
3: syscall read -> 965
3: syscall read -> 453
3: syscall read -> 0
```

## Part 3 - Play with the mask

### 3.1 All the calls

```
$ trace 2147483647 grep hello README
4: syscall trace -> 0
4: syscall exec -> 3
4: syscall open -> 3
4: syscall read -> 1023
4: syscall read -> 965
4: syscall read -> 453
4: syscall read -> 0
4: syscall close -> 0
```

`trace` itself is printed, because the mask is set during that call and checked right after it.

### 3.2 Only fork (mask 2)

```
$ trace 2 usertests forkforkfork
usertests starting
test forkforkfork: 6: syscall fork -> 7
7: syscall fork -> 8
8: syscall fork -> 9
8: syscall fork -> 10
9: syscall fork -> 11
...
8: syscall fork -> 67
9: syscall fork -> -1
8: syscall fork -> -1
OK
ALL TESTS PASSED
```

The forks stop at `-1` when the process table (`NPROC = 64`) is full. In my run five pids printed
fork lines (6, 7, 8, 9 and 10), not three as in the handout. The test's processes all fork in a
loop and xv6 runs on 3 CPUs, so how many of them get to call `fork` before the table fills depends
on the scheduling. The full list is in `trace-output.txt`.

### 3.3 Only write (mask 65536)

```
$ trace 65536 echo hi
hi5: syscall write -> 2

5: syscall write -> 1
```

The pid is 5 here, not 69 as in the handout, because I ran it in a fresh xv6 session.

## Answers (also in `notes.txt`)

1. **Why only `read`, not `open` or `close`?** 32 = 2^5 has only bit 5 on, and 5 is `SYS_read`.
   `open` (15) and `close` (21) still run, but their bits are off, so they are not printed.
2. **Which line lets several pids print in forkforkfork?** `np->trace_mask = p->trace_mask;` in
   `fork()` (`kernel/proc.c`): every child copies its parent's mask, so the whole process tree is
   traced.
3. **Why is the trace line between "hi" and the newline?** xv6 `echo` calls `write` twice: once
   for `hi` (2 bytes) and once for `\n` (1 byte). The kernel prints the trace line right after
   each `write` returns, so it lands between the two.
4. **Mask for `open` and `close` only:** 2^15 + 2^21 = 32768 + 2097152 = **2129920**. Checked:

```
$ trace 2129920 grep hello README
3: syscall open -> 3
3: syscall close -> 0
```

## Files

- `trace.c` - the user program (`user/trace.c`).
- `trace.patch` - the whole Lab 10 diff of the xv6 tree (kernel and user side).
- `Makefile` - the xv6 Makefile with `$U/_trace\` in `UPROGS`.
- `trace-output.txt` - the full output of every command above, from QEMU.
- `notes.txt` - the answers to the "Observe" box.

The optional `sysinfo` system call (not graded) was not done.
