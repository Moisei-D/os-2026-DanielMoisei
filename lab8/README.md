# Lab 8 - The Same Calls, Inside Your Own OS (xv6)

- `run.c` - fork + exec + wait inside xv6 (the child becomes `echo`).
- `pingpong.c` - parent and child exchange one byte through two pipes.
- `primes.c` - optional: prime sieve with a chain of processes.
- `Makefile` - the xv6 Makefile with the `$U/_run\`, `$U/_pingpong\` and `$U/_primes\` lines in `UPROGS`.
- `notes.md` - the answers to the "Observe" boxes.
- `report/` - the LaTeX report (`tectonic Lab8_Moisei_Daniel_FAF241_Report.tex`) and its `figures/`.

Copy the three `.c` files into `~/xv6-riscv/user/`, add the three `UPROGS` lines, then `make qemu`.
