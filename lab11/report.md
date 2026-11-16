# Lab 11 - The Race and the Semaphore

Machine: CachyOS (Linux 7.3), 16 CPU threads, gcc. Every program was compiled with
`gcc -Wall -pthread -o NAME NAME.c` (no `-O2`, as the handout asks). All outputs below are real
runs on this machine.

## Part 1 - See the race

```
$ gcc -Wall -pthread -o race race.c
$ ./race
counter = 1174402 (expected 2000000)
$ ./race
counter = 1249963 (expected 2000000)
$ ./race
counter = 1133683 (expected 2000000)
```

About 40% of the additions are lost, and the number changes every time.

**1. The three steps of `counter++`.** The CPU does load, add, store. This is what gcc generated
for `counter++` in `race` (`objdump -d race`):

```
mov    0x2eb7(%rip),%rax     # 1. load:  read counter from memory into register rax
add    $0x1,%rax             # 2. add:   rax = rax + 1 (only in the register)
mov    %rax,0x2eac(%rip)     # 3. store: write rax back to counter in memory
```

**2. How two threads lose one addition.** Say `counter` is 100:

| Thread A | Thread B | counter in memory |
|----------|----------|-------------------|
| load: rax = 100 | | 100 |
| | load: rax = 100 | 100 |
| add: rax = 101 | | 100 |
| | add: rax = 101 | 100 |
| store: counter = 101 | | 101 |
| | store: counter = 101 | 101 |

Two additions were made, but `counter` went up by only 1: B read the old value before A wrote
its result, and B's store overwrote A's. One addition is lost.

**3. Why the result differs at every run.** The two threads run in parallel on different CPU
cores, and the exact moments when their load/add/store steps overlap depend on scheduling,
interrupts, caches and what else is running. That timing is never the same twice, so the number
of lost additions is different at every run.

## Part 2 - Fix it: mutex, then semaphore

```
$ ./mutex    (3 runs)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
$ ./sem      (3 runs)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
```

The price of the lock (`time ./PROGRAM`, total elapsed time):

| Program | Result | Time |
|---------|--------|------|
| race    | 1056994 (wrong) | 0.026 s |
| mutex   | 2000000 | 0.076 s |
| sem     | 2000000 | 0.102 s |
| atomic (optional) | 2000000 | 0.054 s |

The order is the same as on the reference machine: race < mutex < sem.

**1. Is the answer always 2 000 000?** Yes. All 3 runs of `mutex` and all 3 runs of `sem` printed
exactly 2000000. Only one thread can be between lock and unlock, so the load/add/store of
`counter++` can no longer be interleaved.

**2. What happens with `sem_init(&s, 0, 2)`?** I tried it (3 runs):

```
counter = 1986054 (expected 2000000)
counter = 1988954 (expected 2000000)
counter = 1987171 (expected 2000000)
```

The result is wrong again. With start value 2 the semaphore lets **two** threads pass `sem_wait`
at the same time, and we only have two threads, so both can be inside the critical section
together and the race comes back. Fewer additions are lost than in `race.c` (about 13 000
instead of 800 000) because the `sem_wait`/`sem_post` calls take most of the time, so the two
`counter++` overlap less often, but it is still not correct. To work as a lock, the semaphore
must start at 1.

**3. Why is the locked version slower?** Every addition now also costs a lock and an unlock: atomic
instructions on the lock variable, which must move the cache line between the two cores, and,
when the lock is taken, waiting (and sometimes a `futex` system call to sleep and wake up). The
two threads also no longer add in parallel: they take turns. In `race`, `counter++` is three
plain instructions with no coordination at all, which is why it is fast but wrong.

## Part 3 - A semaphore as a signal

```
$ ./order
B: waiting for the message...
A: message written
B: I read "hello"
```

B printed its first line at once, then there was a 1 second pause, then A and B finished.

**1. Start value 1 (`sem_init(&ready, 0, 1)`).** Output:

```
B: waiting for the message...
B: I read ""
A: message written
```

B reads an **empty string**. The semaphore already has one unit at the start, so B's `sem_wait`
does not block: it takes the unit and B reads `message` at once, while A is still in `sleep(1)`
and has not written anything. `message` is a global array, so it is all zeros, which is an empty
string. The order is no longer guaranteed: the "door" was open from the beginning.

**2. What a semaphore that starts at 0 means.** A semaphore that starts at 0 means "the event has
not happened yet": whoever calls `sem_wait` blocks until another thread calls `sem_post` to
signal that it has happened.

## Part 4 - A semaphore as a counter: the parking lot

```
$ ./parking
car 1 enters (inside: 1)
car 2 enters (inside: 2)
car 3 enters (inside: 3)
car 1 leaves (inside: 2)
car 2 leaves (inside: 1)
car 3 leaves (inside: 0)
car 4 enters (inside: 1)
car 5 enters (inside: 2)
car 6 enters (inside: 3)
car 5 leaves (inside: 2)
car 4 leaves (inside: 1)
car 6 leaves (inside: 0)
```

In my run the first three cars all left before the next three entered (the handout's run mixes
them). Both are correct: the three cars park for the same 1 second, so they leave at almost the
same moment, and the order in which the waiting cars wake up is decided by the scheduler.

**1. The largest value of "inside".** 3. It is guaranteed by `sem_init(&places, 0, PLACES);` with
`PLACES = 3`, together with `sem_wait(&places);` at the entrance of `car()`: the semaphore starts
with 3 units, each car takes one before entering, and the 4th car blocks in `sem_wait` until a
car leaves and calls `sem_post`.

**2. `PLACES` set to 1.** The semaphore becomes a **mutex** (a binary semaphore, like `sem.c` in
Part 2): only one car can be inside at a time. Output:

```
car 1 enters (inside: 1)
car 1 leaves (inside: 0)
car 2 enters (inside: 1)
car 2 leaves (inside: 0)
...
car 6 enters (inside: 1)
car 6 leaves (inside: 0)
```

"inside" never goes above 1, and the program takes about 6 seconds instead of 2.

## Optional - no lock at all (atomic.c)

```
$ time ./atomic
counter = 2000000 (expected 2000000)
0.054 s total
```

Correct, and faster than both the mutex (0.076 s) and the semaphore (0.102 s).
`atomic_fetch_add` makes load, add and store one indivisible CPU instruction (`lock xadd` on
x86), so no other thread can cut in between the steps, and there is no lock to take or wait for.

## Summary: one semaphore, three uses

| Start value | Use | Program |
|-------------|-----|---------|
| 1 | lock (mutual exclusion) | `sem.c` |
| 0 | signal (order: B after A) | `order.c` |
| N | counter (at most N inside) | `parking.c` |
