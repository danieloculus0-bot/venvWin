# venvWin Portable Size Budget

## Benchmark

Puppy Linux around the 2011 era proved that a portable live OS can feel fast, useful, and personal without being a bloated corpse.

venvWin Portable uses that as the design benchmark, but not as a literal byte-for-byte target.

Puppy could stay tiny because it did not ship the same payload venvWin needs:

```text
Wine-compatible runner
Windows app capsule manager
private browser tooling
persistent fake Windows state model
future GUI layer
```

So the rule is:

```text
Respect Puppy. Do not cosplay Puppy.
```

## Size targets

### Alpha

Goal: build and boot first.

```text
Soft warning: > 2500 MB
Hard concern: > 3500 MB
```

At alpha, working beats tiny.

### Beta

Goal: remove obvious bloat.

```text
Target: <= 1600 MB
Stretch: <= 1200 MB
```

### Sellable $8 build

Goal: small enough to feel intentional and portable.

```text
Target: <= 1200 MB
Stretch: <= 900 MB
```

### Puppy-spirit build

Long-term experimental goal.

```text
Target: <= 700 MB
Only possible if we use a much leaner desktop/tooling set or move bulky pieces into optional packs.
```

## Package pressure points

Big likely offenders:

- Wine
- Firefox ESR
- Tor Browser tooling
- full XFCE stack
- Python/pip extras
- firmware packages
- localization files
- docs/manpages/cache leftovers

## Split strategy

The correct mitosis pattern:

```text
Tiny live OS core
Persistent venvWin capsule store
Optional payload packs
```

Possible future split:

```text
venvWin Portable Core
  boots fast
  venvWin CLI
  doctor
  persistence
  EXE/MSI association
  minimal browser or installer stub

venvWin Runner Pack
  Wine runner
  dependency helpers
  known-good profiles

venvWin Privacy Pack
  Tor Browser
  privacy tooling
```

## Product rule

Do not remove the reason venvWin exists just to win a file-size contest.

A 200 MB ISO that cannot run Windows app capsules is just a cute rescue distro with an identity crisis.

## Current priority order

1. boots
2. persists capsule state
3. opens EXE/MSI through venvWin
4. recovers broken capsules
5. feels clean and intentional
6. shrinks without losing the product hook

## Anti-bloat rules

- no Electron by default
- no heavy compositing by default
- no giant office/media suite
- no background indexers
- no full developer toolchain in product image unless needed
- no theme gimmicks that cost performance
- no package included just because it feels nice

## Measurement rule

Every ISO build should report:

- ISO size
- checksum
- package profile
- whether it exceeds alpha warning threshold

If we do not measure it, we are just guessing with confidence, which is how bloated bullshit gets born.
