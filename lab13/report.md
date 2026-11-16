# Lab 13 - Semaphores in Your Own Kernel (xv6)

I added three system calls to my xv6 tree (`~/xv6-riscv`): `sem_init` (24), `sem_down` (25) and
`sem_up` (26). They manage a table of 8 kernel semaphores, shared by all processes. Each semaphore
is a number plus a spinlock that protects it; a process that has to wait really sleeps, using the
kernel's `sleep_prepare` / `sleep` / `wakeup`.

The changes are committed in the xv6 tree as
`450551c Lab 13: kernel semaphores sem_init, sem_down, sem_up (24-26)`.
The same diff is saved here in `sem.patch`. The outputs below are the ones in the screenshots of the
PDF report (`report/Lab13_Moisei_Daniel_FAF241_Report.pdf`).

## Part 1 - The numbers and the user side

| File | Change |
|------|--------|
| `kernel/syscall.h` | `SYS_sem_init 24`, `SYS_sem_down 25`, `SYS_sem_up 26` (22 is `sync`, 23 is `trace` from Lab 10) |
| `user/user.h` | `int sem_init(int, int);`, `int sem_down(int);`, `int sem_up(int);` |
| `user/usys.pl` | `entry("sem_init");`, `entry("sem_down");`, `entry("sem_up");` |
| `user/semtest.c` | the order test and the ping-pong test (see `semtest.c`) |
| `user/mix.c` | two processes printing one letter per `write` (see `mix.c`) |
| `Makefile` | `$U/_semtest\` and `$U/_mix\` in `UPROGS`, after `$U/_zombie\` |

**Check 1.** Before the kernel side existed, the calls reached the kernel, which did not know them
(to reproduce it for the screenshot, the three table entries were commented out, then restored):

```
$ semtest
3 semtest: unknown sys call 24
4 semtest: unknown sys call 25
child: I ran after the parent
parent: done, I let the child go
3 semtest: unknown sys call 26
...
```

Without semaphores the child did not wait: `child:` comes **before** `parent:`, and after these lines
ping and pong were mixed with the error lines.

## Part 2 - The kernel side

| File | Change |
|------|--------|
| `kernel/sem.c` | new file: the table `sems[8]` and `sys_sem_init`, `sys_sem_down`, `sys_sem_up` (see `sem.c`) |
| `Makefile` | `$K/sem.o \` in `OBJS`, after `$K/sysproc.o \` |
| `kernel/syscall.c` | `extern` declarations of the three handlers and their entries in the `syscalls[]` table |

The heart is `sem_down`: while the value is 0 it calls `sleep_prepare(s)` (it will sleep on the
address of `s`), releases the spinlock, calls `sleep()`, then takes the spinlock again and re-checks.
`sem_up` adds 1 and calls `wakeup(s)`.

Because my tree also has `trace` from Lab 10, I added the three names to its `syscallnames[]` table
too. Without them, `trace 2147483647 mix lock` read past the end of that table and the kernel stopped
with `panic: acquire`; with them it prints e.g. `3: syscall sem_init -> 0`.

**Check 2.** Exactly the expected output:

```
$ semtest
parent: done, I let the child go
child: I ran after the parent
ping 1
  pong 1
ping 2
  pong 2
ping 3
  pong 3
semtest: OK
```

The parent waits 10 ticks before it lets the child go, yet the child prints second: it was asleep
in `sem_down`. Ping and pong alternate strictly, three times each.

## Part 3 - A semaphore as a lock: mix

`mix` was run twice without the lock; the screenshots are Figures 3.1 and 3.2 of the PDF report.
In both runs the letters `A` and `b` of the two processes are mixed (mostly `AbAbAb...`), the
lines are broken in different places, and the two runs are mixed differently. Each run starts with
a short series of `A`, written before the second process started, and ends with a line of only `b`:
the first process had already finished its five lines, so the second one wrote its last letters
alone.

With the lock:

```
$ mix lock
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

Every line stays whole (Figure 3.3): exactly 30 letters, then the newline. In this run the first
process wrote all its five lines of `A` before the second wrote its lines of `b`; the order of the
whole lines depends on the scheduler, but no line is broken.

## Answers (also in `notes.txt`)

1. **Why do the letters mix without the lock?** `mix` writes one letter per `write`, so one line
   costs **31 system calls** (30 letters + the newline). Between any two of them the other process
   can write its own letter, and with 3 CPUs the two processes really run at the same time, so their
   letters reach the console interleaved.
2. **Which two lines make one line a critical section?** `sem_down(3);` before the loop that writes
   the line and `sem_up(3);` after it (each under `if (uselock)`). Semaphore 3 starts at 1, so only
   one process at a time can be between them.
3. **Why `while (s->value == 0)` and not `if`?** `wakeup(s)` wakes **every** process sleeping on `s`,
   but `sem_up` added only one unit. If two processes wait, both wake up; the first one to take the
   spinlock takes the unit, and the second finds 0 again. With `while` it goes back to sleep; with
   `if` it would decrement 0 to -1. (A process can also leave `sleep()` because it was killed.)
4. **What if `sem_down` slept holding the spinlock?** The process that should wake it calls
   `sem_up`, which must first `acquire(&s->lock)`. That lock would be held by the sleeper, so
   `sem_up` would spin forever and never reach `wakeup(s)`: a deadlock. A spinlock also turns
   interrupts off on its CPU. In our xv6 it does not even get that far: `sched()` checks that the
   process holds no other spinlock and panics with `sched locks`.

## Files

- `sem.c`, `semtest.c`, `mix.c` - the new kernel and user files.
- `sem.patch` - the whole Lab 13 diff of the xv6 tree.
- `Makefile` - the xv6 Makefile with `$K/sem.o`, `$U/_semtest\` and `$U/_mix\`.
- `notes.txt` - the answers to the "Observe" box.
- `report/` - the PDF report with the screenshots.

The optional `sem_trydown` system call (not graded) was not done.
