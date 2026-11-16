# Lab 13 - Semaphores in Your Own Kernel (xv6)

- `report.md` - the report: every change, the checks and the outputs.
- `notes.txt` - the answers to the "Observe" box.
- `sem.c` - `kernel/sem.c`, the semaphores (sem_init, sem_down, sem_up).
- `semtest.c` - `user/semtest.c`, the order and ping-pong tests.
- `mix.c` - `user/mix.c`, two processes printing with and without a lock.
- `sem.patch` - the full diff of the xv6 tree; apply with `git apply sem.patch` in `~/xv6-riscv`.
- `Makefile` - the xv6 Makefile with `$K/sem.o`, `$U/_semtest\` and `$U/_mix\`.
- `report/` - the LaTeX report and its PDF, with the screenshots in `report/figures/`.
