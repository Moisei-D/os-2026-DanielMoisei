# Lab 17 - Threads Share Memory, and Race

- `fire.c` - two threads add to the same counter a million times each, without a lock.
- `fire4.c` - Part 2: the same race with four threads.
- `report.md` - the answers to the three "Observe" boxes, with the real outputs.
- `report/` - the LaTeX report and its PDF, with the screenshots in `report/figures/`.

Build: `gcc -Wall -Wextra -pthread -o fire fire.c` (same for `fire4.c`).
