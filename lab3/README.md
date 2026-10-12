# Laboratory Work No. 3

This folder contains the graded shell scripts and the completed report for **The Command Line: Shell, Pipes and Text Filters**.

## Structure

- `report.sh` - summarizes a supplied access log and reports failures per user.
- `oneliners.sh` - answers Q1-Q8 and the optional Part 4 bonus.
- `report/Lab3_Moisei_Daniel_FAF241_Report.tex` - Overleaf-ready report source.
- `report/Lab3-SO.pdf` - compiled report with the completed screenshots and observations.
- `report/figures/` - local screenshot assets referenced by the LaTeX source. Figure assets are excluded from Git by the repository `.gitignore`.

## Test the scripts

Generate `access.log` exactly as specified in the laboratory handout, then run:

```bash
bash oneliners.sh
chmod +x report.sh
./report.sh access.log
./report.sh nope.log; echo "exit code: $?"
```

If the report is revised, compile the `.tex` source in Overleaf and update `report/Lab3-SO.pdf` before submission.
