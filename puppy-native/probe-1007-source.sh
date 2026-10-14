#!/usr/bin/env bash
# Discovery and provenance gate for the historically compatible BW64 10.0.7.
# Fail CLOSED. Never silently substitute 10.0.8+ or repackage Debian.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/puppy-1007-baseline"
mkdir -p "$OUT"
LOG="$OUT/source-probe.log"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
NAME=BookwormPup64_10.0.7.iso
CANDIDATES=(
  'https://distro.ibiblio.org/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.7'
  'https://mirror.math.princeton.edu/pub/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.7'
  'https://ftp.nluug.nl/ftp/pub/os/Linux/distr/puppylinux/puppy-bookwormpup/BookwormPup64/10.0.7'
  'https://rockedge.org/kernels/data/ISO/Bookworm_Pup64'
  'https://rockedge.org/kernels/data/ISO/Bookworm_Pup64/64_Bit/legacy'
)
ISO_URL=''
ISO_SHA=''
for base in "${CANDIDATES[@]}"; do
  echo "SOURCE_CANDIDATE=$base"
  checksum="$(curl --fail --location --silent --show-error --max-time 18 "$base/$NAME-checksum.txt" 2>/dev/null || true)"
  # Only a real 64-digit upstream SHA256 line, matching this exact filename.
  sha="$(printf '%s\n' "$checksum" | awk -v f="$NAME" 'length($1)==64 && $1 ~ /^[0-9a-fA-F]+$/ && $2==f {print tolower($1); exit}')"
  if [[ -z "$sha" ]]; then
    echo 'NO_MATCHING_UPSTREAM_SHA256'
    continue
  fi
  head="$(curl --head --location --silent --show-error --max-time 18 "$base/$NAME" || true)"
  if ! grep -Eiq '^HTTP/[0-9.]+ 200([[:space:]]|$)' <<< "$head"; then
    echo 'ISO_NOT_HTTP_200'
    continue
  fi
  ISO_URL="$base/$NAME"
  ISO_SHA="$sha"
  break
done
if [[ -z "$ISO_URL" ]]; then
  echo 'BLOCKER_1007_OFFICIAL_ISO_AND_MATCHING_CHECKSUM_NOT_CURRENTLY_ACCESSIBLE'
  echo 'NO_1008_SUBSTITUTION_NO_GUEST_CLAIM_NO_PUBLICATION'
  exit 27
fi
echo "UPSTREAM_ISO_SOURCE=$ISO_URL"
echo "UPSTREAM_ISO_SHA256=$ISO_SHA"
printf '%s\n' "$ISO_URL" > "$OUT/source-url.txt"
printf '%s  %s\n' "$ISO_SHA" "$NAME" > "$OUT/upstream.sha256"
curl --fail --location --retry 2 --connect-timeout 30 --max-time 1200 \
  -o "$OUT/$NAME.partial" "$ISO_URL"
mv "$OUT/$NAME.partial" "$OUT/$NAME"
(cd "$OUT" && sha256sum -c upstream.sha256)
file "$OUT/$NAME"
echo 'OFFICIAL_1007_IMAGE_SHA256_VERIFIED_NOT_GUEST_PROOF'
# Historical package, do NOT rebuild Wine using contemporary Debian libraries.
WINE_URL='https://archive.org/download/wine-8.0_all_bookwormpup64/wine-8.0_all_bookwormpup64.sfs'
WINE='wine-8.0_all_bookwormpup64.sfs'
curl --fail --location --retry 2 --connect-timeout 30 --max-time 1200 \
  -o "$OUT/$WINE.partial" "$WINE_URL"
mv "$OUT/$WINE.partial" "$OUT/$WINE"
printf '%s  %s\n' '184d623cd08451902b846c24d9c3a8d8' "$OUT/$WINE" | md5sum -c -
file "$OUT/$WINE"
sha256sum "$OUT/$WINE" > "$OUT/wine-sha256.txt"
echo 'WINE80_HISTORICAL_SFS_MATCHED_COMMUNITY_MD5_NOT_GUEST_EXECUTION'
