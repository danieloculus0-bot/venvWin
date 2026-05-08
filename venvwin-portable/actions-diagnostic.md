# GitHub Actions Diagnostic

## Current symptom

The repo has workflow files, but commit-linked workflow runs may not appear through the connector.

This can happen when:

```text
Actions are disabled for the repo
workflow permissions are restricted
push path filters did not match
GitHub has not indexed the run yet
connector cannot see workflow run data
manual workflow_dispatch has not been tapped yet
```

## Required workflow

```text
.github/workflows/flash-ready-standard.yml
```

## Manual phone trigger

Use:

```text
Actions > flash-ready-standard > Run workflow > main
```

## If Run workflow button is missing

Check repo settings:

```text
Settings > Actions > General
```

Required:

```text
Allow all actions and reusable workflows
Workflow permissions: Read and write permissions is preferred for artifact workflows
```

## If workflow runs but fails

Open the failed run and inspect the first failed section:

```text
Install ISO build tools
Run flash-ready standard gate
Upload flash-ready artifacts
```

Most likely failure stages:

```text
pre-ISO readiness gate
live-build dependency/build failure
static ISO inspection
QEMU smoke timeout/early exit
artifact upload
```

## Flash rule

No USB flash until artifact exists and verdict says:

```text
status=FLASH_READY
```
