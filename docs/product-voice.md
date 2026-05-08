# venvWin / venvWin Product Voice

## Goal

venvWin and venvWin should not sound like sterile enterprise software written by a committee that hates oxygen.

The product voice should be:

- useful first
- clear
- mildly unhinged
- technical but not smug
- darkly funny when something breaks
- never confusing for the sake of being funny

## Tone target

```text
Basic Linux utility brain.
Shop-floor troubleshooting mouth.
Dark-mode goblin energy.
```

## Where the voice belongs

Good places:

- help text
- warning messages
- repair/reset copy
- first-run screen
- error summaries
- docs aimed at normal users
- venvWin Portable quick-start guide

Bad places:

- legal/license text
- security boundaries
- crash logs that need exact parsing
- command output consumed by scripts
- JSON output
- API fields

## Words and phrases that fit

Use sparingly:

- bullshit
- goblin
- cursed
- spicy
- misbehaving
- haunted
- not product-ready
- fix the little bastard

## Examples

### Good

```text
Runner missing. venvWin can still create capsules, but it cannot launch Windows apps until the runner is installed. The plumbing exists. The engine is missing.
```

```text
This capsule looks haunted. Try Snapshot, Reset, or Repair before nuking the whole damn thing.
```

```text
Disposable session detected. Anything you install may vanish after reboot. That is fine for testing and terrible for keeping your work.
```

```text
EXE/MSI handlers are missing. Run `venvwin associate` so double-clicking Windows files stops being bullshit.
```

### Too much

```text
THE SYSTEM IS POSSESSED BY DEMONS AND BILL GATES OWES US MONEY
```

Funny, but useless.

## Help text rule

The first sentence must explain the problem. The second sentence can have attitude.

Example:

```text
No capsules found. Create one with `venvwin create "App Name"`, then we can start fixing this empty little goblin cave.
```

## GUI rule

The GUI can be witty, but it must stay premium.

A dark, clean interface with one sharp line is better than a pile of meme text.

## Commercial rule

venvWin Portable can be weird enough to be memorable, but not so weird that an $8 customer thinks it is malware, vaporware, or a joke project.

## Hard boundary

Do not hide behavior behind jokes. Every message must still clearly tell the user what happened and what to do next.
