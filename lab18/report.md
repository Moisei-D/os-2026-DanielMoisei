# Lab 18 - A User-Level Thread Switch (xv6)

I built a tiny thread library in user space: `uthread` creates three threads and switches between
them by saving and restoring registers, like the kernel's `swtch`, but entirely in the program's own
code. There are no kernel changes.

The changes are committed in the xv6 tree as
`903ec37 Lab 18: user-level threads uthread with thread_switch`.
The same diff is saved here in `uthread.patch`, and the full output in `uthread-output.txt`.

## Part 1 - The switch

### 1.1 user/uthread.c

The three TODO places of the skeleton:

**`struct context`** - the 14 callee-saved registers, in the order `thread_switch` uses
(offsets 0, 8, ..., 104):

```c
struct context {
  uint64 ra;
  uint64 sp;
  uint64 s0;
  uint64 s1;
  ...
  uint64 s11;
};
```

**`thread_create`** - the first switch to a new thread must "return" into its function, on its own
stack. The stack grows down, so `sp` starts at the top of the thread's stack array:

```c
  t->ctx.ra = (uint64)func;
  t->ctx.sp = (uint64)(t->stack + STACK_SIZE);
```

**`thread_schedule`** - mark the next thread running, remember the old one, make the next one
current, and switch:

```c
  if (current_thread != next_thread) {         /* switch threads? */
    struct thread *old = current_thread;
    next_thread->state = RUNNING;
    current_thread = next_thread;
    thread_switch(&old->ctx, &next_thread->ctx);
  }
```

`thread_b` and `thread_c` are copies of `thread_a` with `a` changed to `b` (resp. `c`); `b` waits for
`a` and `c` to start, `c` waits for `a` and `b`.

### 1.2 user/uthread_switch.S

`thread_switch(old, new)` has the shape of the kernel's `swtch`: 14 `sd` instructions save `ra`, `sp`,
`s0`..`s11` of the current thread at offsets 0..104 of `old` (`a0`), 14 `ld` instructions load the
same registers of the next thread from `new` (`a1`), and `ret` returns into the next thread. See
`uthread_switch.S`.

### 1.3 Makefile

`$U/_uthread\` in `UPROGS`, and at the end of the file the rule that links `uthread.o` together with
`uthread_switch.o`:

```make
$U/_uthread: $U/uthread.o $U/uthread_switch.o $(ULIB) $U/user.ld
	$(LD) $(LDFLAGS) -T $U/user.ld -o $U/_uthread $U/uthread.o $U/uthread_switch.o $(ULIB)
	$(OBJDUMP) -S $U/_uthread > $U/uthread.asm
```

## Part 2 - Run it

```
$ uthread
thread_a started
thread_b started
thread_c started
thread_c 0
thread_a 0
thread_b 0
thread_c 1
thread_a 1
thread_b 1
thread_c 2
thread_a 2
thread_b 2
...
thread_c 99
thread_a 99
thread_b 99
thread_c: exit after 100
thread_a: exit after 100
thread_b: exit after 100
thread_schedule: no runnable threads
```

Exactly the expected output. Each thread prints its `started` line and yields until the other two
have started. Then the three take turns in round-robin order, c, a, b, because each `thread_yield`
switches to the next runnable thread after the current one. Each counts from 0 to 99 and exits after
100. When the last one has exited, no thread is runnable and `thread_schedule` ends the program.
`thread_c` counts first because, when `c` starts, it finds `a` and `b` already started and goes
straight into its loop.

## Answer (also in `notes.txt`)

**What does `thread_switch` save and load? Why is `ra` the register that makes execution continue in
the other thread?**

It saves the 14 callee-saved registers of the running thread into `old`: `ra` (the return address),
`sp` (the stack pointer) and `s0`..`s11`. Then it loads the same 14 registers of the next thread from
`new` and executes `ret`. These are enough because `thread_switch` is called like a normal C
function, so the compiler has already saved every caller-saved register (`t0`-`t6`, `a0`-`a7`) that
the caller still needs, on the caller's own stack. Loading `sp` moves to the other thread's stack,
where its own saved values and local variables are.

`ret` means "jump to the address in `ra`". After the loads, `ra` holds the next thread's return
address, so `ret` does not return into the thread that called `thread_switch` but into the other
one: for a thread that ran before, right after its own call to `thread_switch` inside
`thread_schedule`; for a new thread, to the start of its function, because `thread_create` set
`ctx.ra = func` and `ctx.sp` = the top of its own stack.
