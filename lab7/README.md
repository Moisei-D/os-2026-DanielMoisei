# Lab 7 - Three Small Programs: Processes, Redirection, a Pipe

- `run.c` - fork + exec + wait (`ls -l`).
- `zombie.c` - the same, with `sleep(20)` before `waitpid`, to create a zombie.
- `redirect.c` - `ls -l > out.txt` done by hand with `close` + `open`.
- `pipeline.c` - `ls /etc | wc -l` with `pipe`, two `fork`s and `dup`.
- `pipeline3.c` - optional: `ls /usr/bin | grep x | wc -l` with two pipes.
- `report.md` - the answers to the "Observe" boxes.
- `report/` - the LaTeX report (`tectonic Lab7_Moisei_Daniel_FAF241_Report.tex`) and its `figures/`.

Build: `gcc -Wall -Wextra -o run run.c` (same for the others).
