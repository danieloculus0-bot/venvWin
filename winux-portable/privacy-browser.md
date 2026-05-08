# WinUx Portable Privacy Browser Plan

## Goal

WinUx Portable should include a privacy-focused browser path by default.

The preferred path is Tor Browser, not a normal browser shoved through Tor and marketed like magic.

## Product rule

```text
Private Browser = Tor Browser when available.
Firefox over Tor = fallback/experimental.
System-wide Tor = optional advanced mode, not default.
```

## Why not force every browser through Tor?

Forcing normal browsers through Tor can still leak information through:

- DNS behavior
- browser fingerprinting
- plugins/extensions
- WebRTC behavior
- saved sessions
- user mistakes
- non-browser app traffic

That makes fake privacy bullshit. WinUx should not promise what it cannot prove.

## Default user experience

Desktop should include:

```text
WinUx Private Browser
```

Behavior:

1. Try to launch Tor Browser if installed.
2. If Tor Browser Launcher exists, open it.
3. If neither exists, show a clear message and offer fallback instructions.

## Fallback browser mode

A fallback may launch Firefox ESR through Tor/SOCKS tooling only with a warning:

```text
This is not Tor Browser. It may reduce direct exposure, but it is not hardened anonymity. Useful for testing, not spy-movie bullshit.
```

## Advanced mode

Later WinUx may offer:

- route selected apps through Tor
- route specific venvWin capsules through Tor
- disable WebRTC in fallback browser
- DNS leak checks
- network health check
- circuit/status widget

## Not allowed

WinUx should not:

- claim total anonymity
- silently route all traffic through Tor without telling the user
- break normal internet access with no recovery path
- mix privacy marketing with unverifiable claims

## Doctor checks

`venvwin doctor` or a future `winux doctor` should report:

- Tor installed/missing
- Tor Browser Launcher installed/missing
- torsocks/proxychains available/missing
- whether fallback mode is available

## Product voice

Private browsing copy can have attitude, but the privacy claim must stay honest.

Example:

```text
Tor Browser missing. Privacy mode is not ready. Installing a normal browser and calling it anonymous would be bullshit.
```
