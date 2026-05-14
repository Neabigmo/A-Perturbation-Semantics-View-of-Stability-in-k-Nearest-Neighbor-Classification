# TASK-016: Upgrade LaTeX infrastructure

## Owner
Claude Code

## Goal
Make `paper/main.tex` ready for a serious paper draft.

## Required work
1. Add packages needed for figures, tables, theorem environments, hyperlinks,
   clever references, algorithms, and appendices.
2. Add theorem environments:
   - theorem
   - lemma
   - proposition
   - corollary
   - conjecture
   - example
   - remark
3. Add macros for:
   - `\del`
   - `\rep`
   - `\loo`
   - `\add`
   - `\NN`
   - `\loss`
   - `\ind`
   - `\metric`
   - `\sample`
4. Add `paper/sections/00_abstract.tex` if absent.
5. Ensure existing section inputs still compile.
6. Do not write new mathematical claims.

## Validation
`D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper\main.tex`

If `latexmk` is unavailable, record the exact failure.

## Report
Return build result and changed files.
