# Git And Environment

## Environment

Use:

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -V
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

Python compatibility is `>=3.9`.

## LaTeX

Preferred TeX Live installation:

```powershell
D:\texlive\2025
```

When compiling LaTeX, prefer executables under:

```powershell
D:\texlive\2025\bin\windows
```

Preferred paper build command:

```powershell
D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper/main.tex
```

## Proxy

Before network commands:

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "socks5://127.0.0.1:7897"
```

## Git

- Use one branch or worktree per task.
- Include task ids in commit messages.
- Review diffs before commit.
- Never commit `.env`, keys, raw logs, or cache artifacts.
