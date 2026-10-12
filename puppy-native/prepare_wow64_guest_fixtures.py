#!/usr/bin/env python3
"""Keep BEAN's history while recording a distinct WoW64 experiment identity."""
import prepare_guest_wine_fixtures as fixtures

fixtures.RUNTIME = (
    'official-BookwormPup64-10.0.12|kernel-6.1.148|'
    'external-SFS-Kron4ek-wine-11.19-amd64-wow64|sha256:'
    'a1fe858b45d12c9b16b91c7601d9b934f68430f7b6b95e240212ab6e2a198d8a'
)
fixtures.SOURCES = (*fixtures.SOURCES,
    'puppy-native/build-wine-wow64-sfs.sh',
    'puppy-native/venvwin-wine-wow64-guest-lab',
    'puppy-native/prove-wow64-qemu.sh')

if __name__ == '__main__':
    raise SystemExit(fixtures.main())
