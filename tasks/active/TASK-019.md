# TASK-019: BibTeX formatting pass

## Owner
Claude Code

## Goal
Format BibTeX entries provided by Codex.

## Inputs
Use `docs/literature/refs_to_add.bib` if present.

## Required work
1. Merge entries into `paper/refs.bib`.
2. Deduplicate keys.
3. Do not add new references without Codex-provided source.
4. Ensure paper compiles.

## Validation
`D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper\main.tex`

If unavailable, record build blocker.

## Report
Return changed entries and unresolved duplicates.
