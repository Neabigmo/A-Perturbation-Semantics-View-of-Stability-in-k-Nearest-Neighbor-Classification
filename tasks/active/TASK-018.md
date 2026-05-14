# TASK-018: Create appendix scaffolding

## Owner
Claude Code

## Goal
Create appendix files for proofs, enumeration details, and additional figures.

## Required work
Create:
- `paper/sections/A_proofs.tex`
- `paper/sections/B_enumeration_protocol.tex`
- `paper/sections/C_additional_figures.tex`
- `paper/sections/D_bib_notes.tex`

Update `main.tex` to include appendices after discussion.

Do not invent proof content. Use placeholder label:
`Proof to be inserted after Codex audit.`

## Validation
`D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper\main.tex`

If unavailable, record build blocker.

## Report
Return changed files and build result.
