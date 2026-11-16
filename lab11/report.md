# Lab 11 - The Race and the Semaphore

Machine: CachyOS (Linux 7.3), gcc. Every program was compiled with `gcc -Wall -pthread -o NAME NAME.c`
(no `-O2`, as the handout asks) and run in `~/os-lab11`. The outputs below are the ones shown in the
screenshots of the PDF report (`report/Lab11_Moisei_Daniel_FAF241_Report.pdf`).

## Part 1 - See the race

```
$ gcc -Wall -pthread -o race race.c && ./race && ./race && ./race
counter = 1188354 (expected 2000000)
counter = 1111694 (expected 2000000)
counter = 1039394 (expected 2000000)
```

Never 2 000 000, and different at every run: between 40% and 48% of the additions were lost.

**1. The three steps of `counter++`.** The CPU does: **load** the value of `counter` from memory into
a register, **add** 1 to the register, **store** the register back into `counter`.

**2. How two threads lose one addition.** Say `counter` is 100:

| Thread A | Thread B | counter in memory |
|----------|----------|-------------------|
| load: register = 100 | | 100 |
| | load: register = 100 | 100 |
| add: register = 101 | | 100 |
| | add: register = 101 | 100 |
| store: counter = 101 | | 101 |
| | store: counter = 101 | 101 |

Two additions were made, but `counter` went up by only 1: B read the old value before A wrote its
result, and B's store overwrote A's. One addition is lost.

**3. Why the result differs at every run.** The two threads run in parallel on different cores, and
the moments when their load/add/store steps overlap depend on scheduling, interrupts, caches and the
other work of the system. That timing is never the same twice, so the number of lost additions
changes at every run.

## Part 2 - Fix it: mutex, then semaphore

```
$ gcc -Wall -pthread -o mutex mutex.c && ./mutex && ./mutex && ./mutex
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)

$ gcc -Wall -pthread -o sem sem.c && ./sem && ./sem && ./sem
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
counter = 2000000 (expected 2000000)
```

The price of the lock:

```
$ time ./race; time ./mutex; time ./sem
counter = 1114644 (expected 2000000)
./race  0.07s user 0.00s system 190% cpu 0.036 total
counter = 2000000 (expected 2000000)
./mutex  0.10s user 0.04s system 188% cpu 0.078 total
counter = 2000000 (expected 2000000)
./sem  0.14s user 0.07s system 193% cpu 0.107 total
```

| Program | Result | Total time |
|---------|--------|------------|
| race    | 1114644 (wrong) | 0.036 s |
| mutex   | 2000000 | 0.078 s |
| sem     | 2000000 | 0.107 s |

The order is the same as on the reference machine: race < mutex < sem.

**1. Is the answer always 2 000 000?** Yes. All 3 runs of `mutex` and all 3 runs of `sem` printed
exactly 2000000.

**2. What happens with `sem_init(&s, 0, 2)`?** I tried it in a copy, `sem2.c`:

```
$ sed 's/sem_init(&s, 0, 1)/sem_init(\&s, 0, 2)/' sem.c > sem2.c && grep -n "sem_init" sem2.c && gcc -Wall -pthread -o sem2 sem2.c && ./sem2 && ./sem2 && ./sem2
23:    sem_init(&s, 0, 2);         /* 0 = shared between threads, 1 = start value */
counter = 1988218 (expected 2000000)
counter = 1988663 (expected 2000000)
counter = 1988836 (expected 2000000)
```

The result is wrong again. With start value 2 the semaphore lets **two** threads pass `sem_wait` at
the same time, and there are only two threads, so both can be inside the critical section together
and the race comes back. Fewer additions are lost than in `race.c` (about 12 000 instead of about
900 000), because most of the time is spent in `sem_wait`/`sem_post` and the two increments overlap
less often, but it is still not correct. To work as a lock, the semaphore must start at 1.

**3. Why is the locked version slower?** Every addition also costs a lock and an unlock: atomic
operations on a shared variable that must move between the caches of the two cores, and, when the
lock is taken, waiting (sometimes by sleeping in the kernel). The two threads no longer add in
parallel: they take turns.

## Part 3 - A semaphore as a signal

```
$ gcc -Wall -pthread -o order order.c && ./order
B: waiting for the message...
A: message written
B: I read "hello"
```

B printed its first line at once, then there was a 1 second pause, then A and B finished.

**1. Start value 1.** In a copy, `order1.c`:

```
$ sed 's/sem_init(&ready, 0, 0)/sem_init(\&ready, 0, 1)/' order.c > order1.c && grep -n "sem_init" order1.c && gcc -Wall -pthread -o order1 order1.c && ./order1
30:    sem_init(&ready, 0, 1);
B: waiting for the message...
B: I read ""
A: message written
```

B reads an **empty string**. The semaphore already has one unit at the start, so B's `sem_wait` does
not block: B takes the unit and reads `message` at once, while A is still in `sleep(1)` and has not
written anything. `message` is a global array, so it is all zeros, which is an empty string.

**2. What a semaphore that starts at 0 means.** The event has not happened yet: whoever calls
`sem_wait` blocks until another thread calls `sem_post` to signal that it has happened.

## Part 4 - A semaphore as a counter: the parking lot

```
$ gcc -Wall -pthread -o parking parking.c && ./parking
car 1 enters (inside: 1)
car 3 enters (inside: 2)
car 2 enters (inside: 3)
car 1 leaves (inside: 2)
car 3 leaves (inside: 1)
car 4 enters (inside: 2)
car 2 leaves (inside: 1)
car 5 enters (inside: 2)
car 6 enters (inside: 3)
car 6 leaves (inside: 2)
car 4 leaves (inside: 1)
car 5 leaves (inside: 0)
```

Cars 1, 3 and 2 entered first; car 4 entered only after cars 1 and 3 had left, and cars 5 and 6 only
after car 2 had left. The order differs from the handout's example because the scheduler decides it,
but the limit of three is always respected.

**1. The largest value of "inside".** 3. It is guaranteed by `sem_init(&places, 0, PLACES);` with
`PLACES = 3`, together with `sem_wait(&places);` at the entrance of `car()`: the semaphore starts with
3 units, each car takes one before entering, and the 4th car blocks in `sem_wait` until a car leaves
and gives its unit back with `sem_post`.

**2. `PLACES` set to 1.** The semaphore becomes a **mutex** (a binary semaphore, like `sem.c` in
Part 2): only one car can be inside at a time. In a copy, `parking1.c`:

```
$ sed 's/#define PLACES 3/#define PLACES 1/' parking.c > parking1.c && grep -n "define PLACES" parking1.c && gcc -Wall -pthread -o parking1 parking1.c && ./parking1
9:#define PLACES 1
car 1 enters (inside: 1)
car 1 leaves (inside: 0)
car 2 enters (inside: 1)
car 2 leaves (inside: 0)
car 3 enters (inside: 1)
car 3 leaves (inside: 0)
car 4 enters (inside: 1)
car 4 leaves (inside: 0)
car 5 enters (inside: 1)
car 5 leaves (inside: 0)
car 6 enters (inside: 1)
car 6 leaves (inside: 0)
```

## Optional - no lock at all (atomic.c)

```
$ gcc -Wall -pthread -o atomic atomic.c && time ./atomic
counter = 2000000 (expected 2000000)
./atomic  0.11s user 0.00s system 193% cpu 0.056 total
```

Correct, and faster (0.056 s) than both the mutex (0.078 s) and the semaphore (0.107 s).
`atomic_fetch_add` makes load, add and store one indivisible CPU step, so no other thread can cut in
between them, and there is no lock to take or wait for.

## Summary: one semaphore, three uses

| Start value | Use | Program |
|-------------|-----|---------|
| 1 | lock (mutual exclusion) | `sem.c` |
| 0 | signal (order: B after A) | `order.c` |
| N | counter (at most N inside) | `parking.c` |
