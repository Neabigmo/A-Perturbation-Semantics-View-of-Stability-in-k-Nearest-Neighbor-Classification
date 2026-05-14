# TASK-010: Draft LaTeX definitions section

## Owner

Claude Code

## Goal

Draft `paper/sections/03_definitions.tex` from the frozen definitions spec.

## Context

Use only `docs/project-control/02_DEFINITIONS_SPEC.md`.

## Required work

1. Draft definitions in paper style.
2. Mark any unresolved claim as `Claim under review`.
3. Compile if LaTeX tooling is available.

## Do not do

- Do not invent theorem statements.
- Do not alter the frozen spec.

## Validation

```powershell
D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper/main.tex
```

If `latexmk` is unavailable, report that plainly.

## Report

Return sections modified, theorem/lemma numbers added, unproved claims, and compile result.
