# Lab 17 - Threads Share Memory, and Race

Machine: CachyOS (Linux 7.3), gcc. Every program was compiled with
`gcc -Wall -Wextra -pthread -o NAME NAME.c` and run in `~/os-lab17`. The outputs below are the ones
shown in the screenshots of the PDF report (`report/Lab17_Moisei_Daniel_FAF241_Report.pdf`).

## Part 1 - Shared and racing

```
$ gcc -Wall -Wextra -pthread -o fire fire.c && ./fire && ./fire && ./fire
thread 1 sees counter = 0
thread 2 sees counter = 0
expected: 2000000
counter: 1016406    (lost updates: the race)
thread 1 sees counter = 0
thread 2 sees counter = 15220
expected: 2000000
counter: 991935    (lost updates: the race)
thread 1 sees counter = 0
thread 2 sees counter = 0
expected: 2000000
counter: 1046364    (lost updates: the race)
```

Always less than 2 000 000 and different every run: about half of the additions were lost.

On this machine thread 2 usually prints 0 at the start: the two threads are created almost at the
same moment and run on different cores, so thread 2 reads the counter before thread 1 has added
anything. In the second run above it started a little later and saw 15220. Running the program 20
times and keeping only thread 2's line:

```
$ for i in $(seq 20); do ./fire | sed -n 2p; done
thread 2 sees counter = 52703
thread 2 sees counter = 0
... (18 more lines, all 0)
```

In 19 of the 20 runs thread 2 saw 0; in the first one it saw 52703.

**Observe: thread 2 prints a non-zero counter at the start. What does that prove about the memory
of the two threads?**
That they share the same memory. Thread 2 reads the value that thread 1 has already written into
`counter`: the threads do not have their own copies of the variable, they work on the one variable
of the process, so a change made by one thread is seen immediately by the other.

**Observe: why is the final counter less than 2000000, and different each run?**
`counter++` is not one step but three:
1. **read** the value of `counter` from memory into a register,
2. **add** 1 to the register,
3. **write** the register back to `counter`.

If both threads read the same value, say 100, before either writes, both write 101: two additions
were made, but the counter grew by only one, so one update is lost. This happens many times during
the two million additions. How often the two threads overlap depends on the exact timing on their
cores (scheduling, interrupts, caches), which is never the same twice, so the result changes every
run and is always below 2 000 000.

## Part 2 - Make it worse, then think

`fire4.c` is the same program with four threads (expected 4 000 000):

```
$ gcc -Wall -Wextra -pthread -o fire4 fire4.c && ./fire4 && ./fire4 && ./fire4
thread 1 sees counter = 0
thread 2 sees counter = 0
thread 3 sees counter = 0
thread 4 sees counter = 42894
expected: 4000000
counter: 1249827    (lost updates: the race)
thread 1 sees counter = 0
thread 2 sees counter = 0
thread 3 sees counter = 0
thread 4 sees counter = 39404
expected: 4000000
counter: 1214827    (lost updates: the race)
thread 1 sees counter = 0
thread 2 sees counter = 0
thread 3 sees counter = 16988
thread 4 sees counter = 17418
expected: 4000000
counter: 1326509    (lost updates: the race)
```

Yes, the loss gets bigger: with two threads about half of the additions were lost, with four threads
about two thirds (1.21 to 1.33 million out of 4 million). More threads change the counter at the same
time, so overlaps of the read-add-write steps happen more often, and each one loses an update.
(Threads 3 and 4 also show the shared memory again: they start a little later and see the additions
already made by the others.)

**A way to make `counter++` safe (on paper).** The three steps must become indivisible: while one
thread is between the read and the write, no other thread may touch `counter`. Put `counter++` in a
critical section protected by a lock (a mutex): take the lock before the increment, release it
after, so only one thread at a time is inside. (Another way is an atomic CPU instruction that does
the read, the add and the write as one step.)

**Observe: in one sentence, what single idea would stop the lost updates?**
Mutual exclusion: let only one thread at a time execute `counter++`, by protecting it with a lock.
