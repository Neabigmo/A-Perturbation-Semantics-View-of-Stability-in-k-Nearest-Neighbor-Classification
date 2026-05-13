# Computational Minimality Certificate

This document is computational evidence only. It is not a proof.

## Observed Minimal Vertex Counts

- TASK-007 separation witnesses: `2`
- TASK-008 tie-free witnesses: `2`

## Observed No-Solution Vertex Counts

- TASK-007: `[1]`
- TASK-008: `[1]`

## Output Hashes

- `TASK-007`: `5b7a8925688a353159a31c60b7c9579f506a46448382ed1ca9d345e2c2ffa0d1`
- `TASK-008`: `a52aa8a77a9a416b44875740da923da03cb7d19c07974fb3617dca609ce1f12b`

## Reproducibility Commands

- `conda run -p E:\anaconda3\envs\pytorch-clean python experiments/search_minimal_1nn.py --max_vertices 4`
- `E:\anaconda3\envs\pytorch-clean\python.exe experiments/search_tie_free.py --input outputs/witnesses/1nn_separation_witnesses.json --output outputs/witnesses/1nn_tie_free_witnesses.json`
- `conda run -p E:\anaconda3\envs\pytorch-clean python experiments/certify_minimality.py`
