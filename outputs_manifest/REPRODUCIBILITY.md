# Run Reproducibility

- Config: `experiments\configs\ml_submission.toml`
- Git HEAD: `e66b4967e64c1fb08e861e99e4d08169f966c063`
- LaTeX: `D:\texlive\2025\bin\windows\latexmk.exe`
- Figure standard: `external/nature-skills/skills/nature-figure`
- Entry point: `python experiments/run_all.py --config ...`
- Output layout:
  - `raw/`: JSON artifacts from search and benchmark stages
  - `rendered/`: generated figures and LaTeX tables
  - `summaries/`: copied reference/control documents for this run
  - `manifests/`: commands, timestamps, and SHA-256 checksums

