# TASK-009: Generate minimality certificate

## Owner

Claude Code

## Goal

Generate computational no-solution tables, reproducibility commands, and output hashes.

## Context

This is computational evidence only.
Use these accepted inputs:

- `outputs/witnesses/1nn_separation_witnesses.json`
- `outputs/witnesses/1nn_tie_free_witnesses.json`

The certificate in this task is not a proof. It is a deterministic summary of:

- searched vertex ranges;
- no-solution ranges observed within those searches;
- minimal vertex counts observed within those searches;
- reproducibility commands;
- output file hashes.

## Required work

1. Create certificate output files under `outputs/tables/` or `outputs/witnesses/`.
2. Record search ranges and assumptions from TASK-007 and TASK-008.
3. Include hashes for generated outputs.
4. State clearly that the result is computational evidence only.

## Do not do

- Do not call the certificate a proof.
- Do not change search constraints without reporting it.

## Validation

Run pytest and the certificate script.

## Report

Return structured report.
