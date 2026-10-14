#!/usr/bin/env sh
# One bounded read; no creation, automatic retry or redirect following.
set -eu
: "${OLOSTEP_API_KEY:?Set OLOSTEP_API_KEY privately}"
: "${BATCH_ID:?Set BATCH_ID to an existing operation}"
case "$BATCH_ID" in *[!a-zA-Z0-9_-]*) echo 'Invalid batch ID' >&2; exit 2;; esac
curl --fail --silent --show-error --max-time 10 \
  --header "Authorization: Bearer $OLOSTEP_API_KEY" \
  "https://api.olostep.com/v1/batches/$BATCH_ID"
