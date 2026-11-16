# Lab 12 - Producer, Consumer and the Other Tools

Machine: CachyOS (Linux 7.3), gcc. Every program was compiled with `gcc -Wall -pthread -o NAME NAME.c`
and run in `~/os-lab12`. For the questions that ask to change a line, a modified copy was made with
`sed`, so the submitted files stay unchanged. The outputs below are the ones shown in the screenshots
of the PDF report (`report/Lab12_Moisei_Daniel_FAF241_Report.pdf`).

## Part 1 - Producer and consumer

```
$ gcc -Wall -pthread -o prodcons prodcons.c && ./prodcons
put 1    (in buffer: 1)
put 2    (in buffer: 2)
put 3    (in buffer: 3)
put 4    (in buffer: 4)
            take 1   (in buffer: 3)
put 5    (in buffer: 4)
            take 2   (in buffer: 3)
put 6    (in buffer: 4)
            take 3   (in buffer: 3)
put 7    (in buffer: 4)
            take 4   (in buffer: 3)
put 8    (in buffer: 4)
            take 5   (in buffer: 3)
            take 6   (in buffer: 2)
            take 7   (in buffer: 1)
            take 8   (in buffer: 0)
```

Exactly the expected output. The producer fills the 4 slots at once, then follows the slow consumer:
one `put` after each `take`.

**1. Which call stops the producer?** `sem_wait(&empty);`. `empty` starts at 4 (the free slots). Each
`put` takes one unit, so after 4 puts `empty` is 0 and the 5th `sem_wait(&empty)` blocks. The
producer continues only when the consumer frees a slot with `sem_post(&empty)`.

**2. Who waits at the start?** The **consumer**, in `sem_wait(&full);`. `full` starts at 0 because the
buffer is empty, so the consumer blocks until the producer has put the first item and called
`sem_post(&full)`.

**3. Mutex locked before `sem_wait(&empty)`.** In a copy, `prodcons_swap.c`, the first two lines of the
producer's loop were swapped:

```
$ sed '/sem_wait(&empty);/{N;s/\(.*\)\n\(.*\)/\2\n\1/}' prodcons.c > prodcons_swap.c && sed -n '/void \*producer/,/buf\[in\]/p' prodcons_swap.c
void *producer(void *arg) {
    for (int item = 1; item <= ITEMS; item++) {
        pthread_mutex_lock(&lock);
        sem_wait(&empty);               /* wait for a free slot */
        buf[in] = item;
$ gcc -Wall -pthread -o prodcons_swap prodcons_swap.c && ./prodcons_swap
put 1    (in buffer: 1)
put 2    (in buffer: 2)
put 3    (in buffer: 3)
put 4    (in buffer: 4)
^C
```

The program stopped after the buffer was full and had to be stopped with Ctrl-C. It is a **deadlock**:
when the buffer is full, the producer takes the mutex and then sleeps in `sem_wait(&empty)` **while
still holding the mutex**. To free a slot, the consumer must first take that same mutex, so it blocks
in `pthread_mutex_lock(&lock)`. The producer waits for the consumer to free a slot, and the consumer
waits for the producer to release the mutex: neither can ever continue. Here the consumer did not even
manage to take item 1, because the producer re-locked the mutex for the next item faster than the
consumer could get it. The rule: never sleep on a semaphore while holding a mutex the other side needs.

## Part 2 - The condition variable

```
$ gcc -Wall -pthread -o condvar condvar.c && ./condvar
B: not ready, I sleep
A: message written
B: I read "hello"
```

**1. Which variable remembers that the message is ready?** The ordinary variable `int ready`, protected
by the mutex `lock`. The condition variable `changed` remembers nothing: it is only the place where B
sleeps. A `pthread_cond_signal` with nobody waiting is simply lost, which is why B checks `ready`
itself.

**2. With `if (!ready)` instead of `while`.** In a copy, `condvar_if.c`:

```
$ sed 's/while (!ready)/if (!ready)/' condvar.c > condvar_if.c && grep -n 'if (!ready)' condvar_if.c
27:    if (!ready) {                            /* while, not if: re-check after waking */
$ gcc -Wall -pthread -o condvar_if condvar_if.c && ./condvar_if
B: not ready, I sleep
A: message written
B: I read "hello"
```

Yes, it still works here, because there is exactly one writer, it sets `ready = 1` before signalling,
and nothing ever sets `ready` back to 0.

(In zsh the `grep` pattern must be in single quotes: inside double quotes `!ready` is taken as a
history expansion and the whole command is cancelled with `event not found`.)

**3. Why `while`?** Because waking up from `pthread_cond_wait` does not guarantee that the condition is
true:
- **Spurious wakeups:** POSIX allows `pthread_cond_wait` to return even when nobody signalled, so the
  thread must check `ready` again.
- **Another thread got there first:** with several waiting threads, another thread can take the mutex
  first and consume the event before the woken thread runs, so it finds `ready == 0` and must sleep
  again.

## Part 3 - Readers and writers

```
$ gcc -Wall -pthread -o readers readers.c && ./readers
writer 1 writes 10 (alone)
reader 1 reads 10   (readers inside: 1)
reader 2 reads 10   (readers inside: 2)
reader 3 reads 10   (readers inside: 3)
writer 2 writes 20 (alone)
```

The three readers are inside at the same time; each writer is alone.

**1. Which two lines make it possible?**

```c
    if (++readers == 1)         /* the first reader in locks out the writers */
        sem_wait(&room);
...
    if (--readers == 0)         /* the last reader out lets the writers in */
        sem_post(&room);
```

Only the **first** reader takes `room`, for the whole group, so the readers that follow enter without
waiting for it; only the **last** reader out gives it back. A writer does `sem_wait(&room)` itself, so
it can enter only when no reader and no other writer is inside.

**2. Why does `readers` need its own lock (`rlock`)?** `++readers` and `--readers` are load, add and
store, like `counter++` in Lab 11. Without `rlock`, two readers arriving together could both read 0 and
both store 1, so both would believe they are first and the count would be wrong. A wrong count can
reach 0 while a reader is still inside, releasing `room` too early and letting a writer in during a
read, or never reach 0, so `room` is never released and the writers wait forever.

**3. Readers that keep arriving without a pause.** Writer 2 waits **forever**. While at least one
reader is inside, `readers` never drops to 0, so `room` is never released, and new readers can still
enter because only the first one needed `room`. The writer is ready but never gets its turn: this is
**starvation**.

## Part 4 - Build a deadlock, then remove it

The submitted `deadlock.c` is the fixed version, so the original was recreated in a copy,
`deadlock_orig.c`, where `two()` takes B first:

```
$ sed '/the fix/s/&A/\&B/; /waits for one/s/&B/\&A/' deadlock.c > deadlock_orig.c && grep -n "the fix\|waits for one" deadlock_orig.c
25:    pthread_mutex_lock(&B);             /* the fix: lock A first here too */
28:    pthread_mutex_lock(&A);             /* waits for one */
$ gcc -Wall -pthread -o deadlock_orig deadlock_orig.c && timeout 5 ./deadlock_orig; echo "exit code: $?"
one: I have A, I want B
two: I have B, I want A
exit code: 124
```

The two lines, then nothing for 5 seconds, then `timeout` killed it (124).

Fixed version (both threads take A first, then B):

```
$ gcc -Wall -pthread -o deadlock deadlock.c && timeout 5 ./deadlock; echo "exit code: $?"
one: I have A, I want B
one: I have both
two: I have B, I want A
two: I have both
done
exit code: 0
```

(The text of two's first line was left as in the handout; in the fixed version two actually holds A at
that moment.)

**1. Who holds what, and who waits for what.** Thread `one` holds mutex **A** and waits for **B**.
Thread `two` holds mutex **B** and waits for **A**. The circle:

```
  one --holds--> A <--waits for-- two
   |                               |
 waits for                       holds
   |                               |
   +-----------> B <---------------+
```

**2. Without the two `sleep(1)` lines.** In a copy, `deadlock_nosleep.c`, run ten times (124 = hung,
0 = finished):

```
$ sed '/sleep(1);/d' deadlock_orig.c > deadlock_nosleep.c && grep -c "sleep(1)" deadlock_nosleep.c
0
$ gcc -Wall -pthread -o deadlock_nosleep deadlock_nosleep.c && for i in $(seq 10); do timeout 2 ./deadlock_nosleep > /dev/null; echo -n "$? "; done; echo
124 124 124 124 124 124 124 124 124 124
```

In these ten runs it still hung every time, but it is no longer guaranteed to hang: whether it hangs
now depends only on timing. If `one` takes both mutexes before `two` takes B, the program ends;
otherwise it hangs. On this machine the two threads start almost at the same moment on different
cores, so they usually both get their first mutex and hang; in earlier test runs on the same machine
the result was not always the same (in one series of ten runs, one finished with exit code 0).

This is **worse**, not better: the bug is still there, but now it is intermittent. A program that
sometimes works can pass a test, is hard to reproduce and debug, and can hang later on another
machine, under another load, or in production. With `sleep(1)` the deadlock happened every time,
which made it easy to see and to fix.

**3. Why the same order never deadlocks.** If every thread takes the locks in the same order (A before
B), a thread that holds B already holds A, so nobody can hold B while waiting for A, and a circle of
waiting can never close.
