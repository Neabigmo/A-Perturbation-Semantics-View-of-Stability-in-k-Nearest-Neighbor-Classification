# Reproducibility

## Environment

- Repository root: `H:\2026try\5.13`
- Git revision at regeneration time: `f4a1932`
- Python executable: `E:\anaconda3\envs\pytorch-clean\python.exe`
- Python version: `3.9.25`
- Key packages:
  - `numpy==1.26.4`
  - `pytest==8.4.2`
  - `matplotlib==3.9.4`
  - `networkx==3.2.1`
- Preferred LaTeX executable:
  `D:\texlive\2025\bin\windows\latexmk.exe`

## Test Command

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe -m pytest
```

Current status:

- `166 passed`
- log: `outputs/logs/task017_pytest.log`

## Experiment Commands

Minimal 1-NN witness search:

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe experiments\search_minimal_1nn.py --max_vertices 4
```

Tie-free witness filtering:

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe experiments\search_tie_free.py --input outputs\witnesses\1nn_separation_witnesses.json --output outputs\witnesses\1nn_tie_free_witnesses.json
```

Minimality certificate:

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe experiments\certify_minimality.py --separation outputs\witnesses\1nn_separation_witnesses.json --tie_free outputs\witnesses\1nn_tie_free_witnesses.json --json_output outputs\witnesses\1nn_minimality_certificate.json --markdown_output outputs\tables\1nn_minimality_certificate.md
```

Odd-k gadget candidate search:

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe experiments\search_k_gadgets.py --k_values 3 5 7 --min_vertices 2 --max_vertices 2 --length_modes equal_k --max_candidates_per_k 3
```

## Figure And Table Commands

Current repository status:

- witness figure script exists: `experiments/generate_witness_figures.py`
- full paper figure script: not yet implemented
- full paper table script: not yet implemented

Scheduled follow-up tasks:

- `tasks/active/TASK-014.md`
- `tasks/active/TASK-015.md`

## LaTeX Build Command

```powershell
D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper\main.tex
```

Current status:

- the current paper source still builds successfully
- the active reading copy is the repository-root `main.pdf`
- the last archived paper build copy is stored under `archive/build/paper_main/`
- bibliography now resolves for the current related-work pass
- current warning level is low; one overfull hbox remains in the related-work section

## Output Hashes

- `outputs/witnesses/1nn_separation_witnesses.json`
  - `5B7A8925688A353159A31C60B7C9579F506A46448382ED1CA9D345E2C2FFA0D1`
- `outputs/witnesses/1nn_tie_free_witnesses.json`
  - `A52AA8A77A9A416B44875740DA923DA03CB7D19C07974FB3617DCA609CE1F12B`
- `outputs/witnesses/1nn_minimality_certificate.json`
  - `92F85B16F79D6FAD24D08F4F087688650057DE0B39B305B4B45AF539B8F8AE93`
- `outputs/witnesses/k_gadget_candidates.json`
  - `B3204D99A02A25048C1A660EC8D0E5AE3344FFA9C6143B660E1665BCCE71BA9B`

## Logs

- `outputs/logs/task017_pytest.log`
- `outputs/logs/task017_search_minimal_1nn.log`
- `outputs/logs/task017_search_tie_free.log`
- `outputs/logs/task017_certify_minimality.log`
- `outputs/logs/task017_search_k_gadgets.log`

## Non-Determinism

No randomness is currently used in the regenerated witness and certificate
pipeline.

## Network Notes

The reproduction commands above do not require network access. If later stages
need network commands, set:

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "socks5://127.0.0.1:7897"
```

## Interpretation Boundary

The witness and certificate artifacts are computational evidence. They are not
theorem-level proofs unless the paper explicitly upgrades a statement after a
separate Codex proof audit.
