#!/usr/bin/env python3
"""New runtime fingerprint: BEAN must never reuse Wine11 WoW64 failures as Debian Wine8 results."""
import prepare_guest_wine_fixtures as fixtures

fixtures.RUNTIME = (
    "official-BookwormPup64-10.0.12|kernel-6.1.148|"
    "external-SFS-official-Debian-Bookworm-wine64-8.0-repack-4|"
    "sha256:4ff56d97fb84c41dd450775f03ae42208f092e822f9baa742dcde951773ecb42|"
    "sha256:512b715f32fccf2ebec2b63f23d9d83394d30e27cc5570a8ef92c5d3627ef305"
)
fixtures.SOURCES = (*fixtures.SOURCES,
    "puppy-native/build-bookworm-wine64-sfs.sh",
    "puppy-native/venvwin-wine-bookworm-guest-lab",
    "puppy-native/prove-bookworm-wine64-qemu.sh")
if __name__ == "__main__":
    raise SystemExit(fixtures.main())
