# Lab 12 - Producer, Consumer and the Other Tools

- `prodcons.c` - producer and consumer around a 4-slot buffer (two semaphores and a mutex).
- `condvar.c` - the `order.c` problem from Lab 11 with a mutex and a condition variable.
- `readers.c` - readers and writers with two semaphores.
- `deadlock.c` - the fixed version: both threads take mutex A, then B.
- `report.md` - the answers to the "Observe" boxes, with the real outputs.
- `report/` - the LaTeX report and its PDF, with the screenshots in `report/figures/`.

Build: `gcc -Wall -pthread -o prodcons prodcons.c` (same for the others).
