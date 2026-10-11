"""Minimal BEAN Core package loader for venvWin Portable.

The full upstream bean.cognition package eagerly imports 20+ optional engines.
This minimal distribution explicitly imports the *unmodified* BEAN epistemic
guard directly, without fake stand-ins or new third-party dependencies.
See puppy-native/BEAN-LOCAL.md for the mirrored source module list.
"""
