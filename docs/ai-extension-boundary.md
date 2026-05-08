# Future AI Extension Boundary

## Purpose

This document reserves a future extension seam for AI-assisted behavior inside venvWin / venvWin.

It is not a backdoor. It is not remote access. It is not a hidden control channel. It is not a self-modification system.

It is a clean architectural boundary for future work if user-granted permissions, platform rules, and project policy later allow more capable AI-assisted tooling.

## Current status

Disabled.

No AI extension runtime exists in the current project.

## Allowed future uses

Potential future AI-assisted features may include:

- compatibility profile suggestions
- installer diagnosis
- capsule repair guidance
- error log summarization
- recommended runner settings
- safe first-run walkthroughs
- local-only troubleshooting helpers

## Not allowed

The extension boundary must not be used for:

- hidden access
- unauthorized remote control
- bypassing user permissions
- self-replication
- silent self-modification
- persistence outside normal project/user consent
- hiding behavior from the user
- changing capsule state without explicit user action

## Design rule

Any future AI capability must be:

- user-visible
- permissioned
- auditable
- reversible where practical
- disabled by default unless intentionally enabled
- documented in release notes

## Reserved interface idea

Future extension modules may receive only explicit inputs such as:

```text
capsule metadata
install logs
runner profile
error output
user-approved diagnostic bundle
```

Future extension modules may return only explicit recommendations or user-approved actions.

## Hard boundary

venvWin can leave a doorframe for future AI. It must not install a secret door.
