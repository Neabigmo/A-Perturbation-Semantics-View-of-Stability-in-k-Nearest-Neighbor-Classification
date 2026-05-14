# TASK-011: Generate figures for witnesses

## Owner

Claude Code ✅

## Status

**Completed**

## Goal

Generate clear graph figures from accepted witness JSON.

## Context

Use witness files supplied by Codex or produced by accepted tasks.
Use these accepted inputs:

- `outputs/witnesses/1nn_separation_witnesses.json`
- `outputs/witnesses/1nn_tie_free_witnesses.json`

Generate figures for the minimal accepted witness. Do not edit the JSON files.

## Required work

1. Generate PDF/SVG figures under `outputs/figures/`.
2. Include labels and tie-breaking annotations if needed.
3. Save the command used.

## Do not do

- Do not alter witness data.
- Do not change theorem statements.

## Validation

Run the figure script and pytest.

## Report

Return files changed, output paths, commands, and ambiguities.
