# Lab 18 - A User-Level Thread Switch (xv6)

- `report.md` - the report: the three edits, the output and the answer.
- `notes.txt` - the answer to the "Observe" box.
- `uthread.c` - `user/uthread.c`, the thread library and the three threads a, b and c.
- `uthread_switch.S` - `user/uthread_switch.S`, `thread_switch` (save and load ra, sp, s0..s11).
- `uthread.patch` - the full diff of the xv6 tree; apply with `git apply uthread.patch` in `~/xv6-riscv`.
- `Makefile` - the xv6 Makefile with `$U/_uthread\` in `UPROGS` and the `_uthread` rule.
- `uthread-output.txt` - the full output of `uthread` in QEMU.
- `report/` - the LaTeX report and its PDF, with the screenshots in `report/figures/`.

No kernel changes: everything runs in user space.
