# Lab 11 - The Race and the Semaphore

- `race.c` - two threads increment a shared counter with no protection (wrong result).
- `mutex.c` - the same counter protected by a mutex.
- `sem.c` - the same counter protected by a semaphore that starts at 1.
- `order.c` - a semaphore that starts at 0 used as a signal.
- `parking.c` - a semaphore that starts at 3 used as a counter.
- `atomic.c` - optional: the counter with `atomic_fetch_add`, no lock.
- `report.md` - the answers to the "Observe" boxes, with the real outputs.
- `report/` - the LaTeX report and its PDF, with the screenshots in `report/figures/`.

Build: `gcc -Wall -pthread -o race race.c` (same for the others, no `-O2`).
