# Laboratory Work No. 3

This folder contains the graded shell scripts and the LaTeX source for the report.

## Structure

- `report.sh` - summarizes a supplied access log and reports failures per user.
- `oneliners.sh` - answers Q1-Q8 and the optional Part 4 bonus.
- `report/Lab3_Moisei_Daniel_FAF241_Report.tex` - Overleaf-ready report source.
- `report/figures/` - place screenshots here using the filenames listed in `figures/README.md`.

## Test the scripts

Generate `access.log` exactly as specified in the laboratory handout, then run:

```bash
bash oneliners.sh
chmod +x report.sh
./report.sh access.log
./report.sh nope.log; echo "exit code: $?"
```

Before submitting, verify all machine-specific values in the report against your own terminal output, replace every screenshot placeholder, compile the `.tex` file in Overleaf, and export it to the format required by the teacher.
