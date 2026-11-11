# BEAN integration deferred by design
The portable venvWin OS does not install BEAN Core or start any BEAN service.
BEAN can be launched manually from its own repository, independently of venvWin.
This is a deliberate user-approved product boundary: no model weights,
background agent startup, cloud API, credential sharing, or hidden service.
Any future integration requires a separate decision and a real guest acceptance gate.
