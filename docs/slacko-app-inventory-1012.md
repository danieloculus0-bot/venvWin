# BookwormPup64 10.0.12 original software inventory — verified

Original ISO checksum-verified; original compressed SFS layers inspected in GitHub Actions run https://github.com/danieloculus0-bot/venvWin/actions/runs/38501751765 .

**Evidence level: package presence, NOT successful guest execution.**

## Good original Slacko functionality ALREADY included in genuine modern Puppy

- AbiWord executable and desktop menu entry present.
- Gnumeric 1.12.48 and ssconvert executable present. XLSX reading/editing/export still need an in-guest roundtrip test.
- Firefox ESR Portable in the original adrv and desktop menu. The Firefox-internal browser/chrome executable is NOT a separately installed Chromium browser; false positive corrected in inventory detection.
- Frisbee, ConnMan GTK and Internet Connection Wizard menu entries present; Wi-Fi/Ethernet actual GUI connectivity still requires guest test.
- JWM and ROX-Filer present; preserve Puppy boot, taskbar, native window management and persistence.
- mtPaint, Viewnior and Pup-Kview present.
- SMPlayer and mpv installed: keep one real GUI playback player with its mpv engine, audio subsystem and codecs.
- Claws Mail installed; leave unless explicitly excluded. User values functional network access over included mail applications.
- ALSA and PipeWire components installed and protected.

## User-approved removal candidates (actual packages observed)

- mhWaveEdit standalone audio editor
- EasyTAG audio metadata editor
- QWinFF video conversion frontend, retain shared ffmpeg codecs
- SimpleScreenRecorder frontend, retain essential video/display APIs
- DeaDBeeF duplicate audio player, retain SMPlayer+mpv
- Celluloid duplicate video player
- Duplicate enqueue-in-SMPlayer desktop entry, retain SMPlayer
- Bundled games including Hexalate, iQPuzzle, PicPuz, Rubix, Simsu and Solitaire

No core libraries, kernel/firmware drivers, Wine/WoW64 libraries, GUI, browser, net-management tools, Gnumeric, AbiWord, filemanager or Puppy boot/persistence may be removed to chase size. Only exact application-specific files may be pruned in an isolated test SFS, using identical original squashfs codec settings and measured before/after bytes.

## Actual original ISO compressed SFS byte counts

- puppy_dpupbw64_10.0.12.sfs: 469,794,816
- adrv_dpupbw64_10.0.12.sfs: 93,790,208
- bdrv_dpupbw64_10.0.12.sfs: 10,711,040
- fdrv_dpupbw64_10.0.12.sfs: 114,696,192
- kbuild-6.1.148.sfs: 15,831,040
- zdrv_dpupbw64_10.0.12.sfs: 75,051,008

**Baseline compatibility barrier:** Both original BookwormPup64 10.0.8 and 10.0.12 plus archived Wine 9.19 guest workflows failed to produce guest-origin proof of Windows PE32/PE32+ execution, despite successful original ISO and Wine package preparation. Guest-origin serial output was empty. No subsequent app trim may be called Wine-tested until the actual guest boot and Windows execution gates pass.

Required further in-guest evidence: Linux GUI and taskbar, Gnumeric XLSX import/edit/export, AbiWord opening, Firefox launch, graphical networking, Windows 32/64 EXE+MSI installation/launch and post-reboot persistence. NO release or main merge before proof.
