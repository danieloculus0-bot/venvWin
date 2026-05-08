# venvWin Standard Build Send Marker

Purpose: trigger the first-boot product gate workflow for the standard profile.

Target workflow:

```text
build-venvwin-iso
profile: standard
qemu_smoke: true
```

Required pass:

```text
ISO builds
desktop boots far enough for smoke
first-boot GUI included
leave-no-trace default included
checksum and manifest generated
```

This marker can be deleted after workflow validation.
