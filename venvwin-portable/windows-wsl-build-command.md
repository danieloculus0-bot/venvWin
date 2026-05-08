# Windows WSL Build Command

Use this when building venvWin Portable from a Windows machine with WSL Ubuntu installed.

## PowerShell from repo root

```powershell
wsl bash -lc "cd /mnt/c/path/to/venvWin && chmod +x venvwin-portable/bootstrap-flash-ready-ubuntu.sh && ./venvwin-portable/bootstrap-flash-ready-ubuntu.sh"
```

Replace:

```text
/mnt/c/path/to/venvWin
```

with the actual WSL path to the repo.

Example if repo is in:

```text
C:\Users\Daniel\venvWin
```

Use:

```powershell
wsl bash -lc "cd /mnt/c/Users/Daniel/venvWin && chmod +x venvwin-portable/bootstrap-flash-ready-ubuntu.sh && ./venvwin-portable/bootstrap-flash-ready-ubuntu.sh"
```

## Success output

The final output must include:

```text
status=FLASH_READY
FLASH READY: dist/venvwin-portable-alpha-standard.iso
```

## Output bundle

```text
dist/venvwin-portable-alpha-standard.iso
dist/venvwin-portable-alpha-standard.iso.sha256
dist/venvwin-portable-alpha-standard-manifest.txt
dist/venvwin-flash-ready-verdict.txt
```

## Rule

Do not flash the USB until:

```powershell
wsl bash -lc "cd /mnt/c/Users/Daniel/venvWin && cat dist/venvwin-flash-ready-verdict.txt"
```

shows:

```text
status=FLASH_READY
```
