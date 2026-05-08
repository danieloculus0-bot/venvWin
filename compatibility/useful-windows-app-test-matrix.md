# Useful Windows App Test Matrix

## Purpose

venvWin needs to test against useful real-world Windows apps, not only toy installers.

The goal is to prove practical value app by app.

## Compatibility lanes

### Lane 1: Simple desktop EXE/MSI

Best first tests.

Examples:

- Notepad++
- 7-Zip
- IrfanView
- VLC
- FreeCAD
- PrusaSlicer
- OrcaSlicer
- Meshmixer legacy installer if available

Expected:

```text
Double-click installer
Capsule created
Install runs
Launcher created
App reopens from capsule
State persists after reboot
```

### Lane 2: Graphics / 3D / CAD utility apps

Important for venvWin because the product should be useful to makers.

Examples:

- Microsoft 3D Viewer style test target
- FreeCAD
- Blender Windows build
- PrusaSlicer
- OrcaSlicer
- OpenSCAD
- MeshLab
- UVtools

Expected:

```text
App launches
OpenGL/Vulkan status visible
File open works
STL/3MF/OBJ association can be tested
Settings persist
```

### Lane 3: Microsoft Store / UWP apps

Hard lane.

Microsoft 3D Viewer likely belongs here if installed as a Store/UWP app rather than a traditional EXE/MSI.

Expected first result:

```text
Not supported yet, but detected clearly.
```

Required future method:

```text
Detect Store/UWP package type
Explain limitation
Offer equivalent desktop test app
Track as separate compatibility engine problem
```

### Lane 4: Heavy commercial apps

Future only.

Examples:

- Fusion 360
- SolidWorks viewer/helper tools
- Adobe utilities
- Office apps

Expected:

```text
May require services, web auth, GPU, registry, fonts, DLLs, or licensing components.
Do not promise support early.
```

## Product scoring

Each app gets scored:

```text
0 = not tested
1 = detected only
2 = installer routed
3 = installs
4 = launches
5 = useful workflow works
6 = persists after reboot
7 = clean uninstall/reset/snapshot recovery works
```

## Minimum useful app proof

Before product release, venvWin/venvWin should prove at least:

```text
one text/editor utility
one archive utility
one media/viewer utility
one maker/3D utility
one failed hard-case with honest messaging
```

## First candidate set

| App | Lane | Why test it | Expected early status |
|---|---:|---|---|
| Notepad++ | 1 | simple installer sanity | should install/launch |
| 7-Zip | 1 | file association / utility | should install/launch |
| IrfanView | 1 | lightweight viewer | should install/launch |
| PrusaSlicer | 2 | maker usefulness | likely useful if graphics ok |
| OpenSCAD | 2 | maker/CAD, lightweight | likely useful |
| FreeCAD | 2 | heavier CAD target | maybe installs, graphics risk |
| Microsoft 3D Viewer | 3 | user-requested useful target | likely UWP/Store challenge |

## Rule

A failed app is still useful if venvWin explains the failure correctly.

Bad:

```text
This app does not work.
```

Good:

```text
This appears to be a Microsoft Store/UWP app. venvWin currently supports EXE/MSI desktop installers first. Store/UWP support is tracked as a separate compatibility lane.
```
