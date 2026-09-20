#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")/.." rev-parse --show-toplevel)"
TARGET="${VNCCS_RUNTIME_DIR:-/mnt/c/Users/user/Documents/ComfyUI/custom_nodes/ComfyUI_VNCCS}"
FORK_URL="${VNCCS_FORK_URL:-https://github.com/AcidicSoil/ComfyUI_VNCCS.git}"
UPSTREAM_URL="${VNCCS_UPSTREAM_URL:-https://github.com/AHEKOT/ComfyUI_VNCCS.git}"
SOURCE_HEAD="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"

if [[ -e "$TARGET" && ! -d "$TARGET/.git" ]]; then
  echo "Refusing to deploy over non-git runtime path: $TARGET" >&2
  exit 2
fi

if [[ -d "$TARGET/.git" ]]; then
  if [[ -n "$(git -C "$TARGET" status --porcelain)" ]]; then
    echo "Refusing to overwrite dirty VNCCS runtime checkout: $TARGET" >&2
    git -C "$TARGET" status --short >&2
    exit 3
  fi
  git -C "$TARGET" fetch "$SOURCE_ROOT" HEAD
  git -C "$TARGET" checkout -q main
  git -C "$TARGET" reset --hard FETCH_HEAD >/dev/null
else
  mkdir -p "$(dirname "$TARGET")"
  git clone -q --no-hardlinks "$SOURCE_ROOT" "$TARGET"
fi

git -C "$TARGET" remote set-url origin "$FORK_URL"
if git -C "$TARGET" remote get-url upstream >/dev/null 2>&1; then
  git -C "$TARGET" remote set-url upstream "$UPSTREAM_URL"
else
  git -C "$TARGET" remote add upstream "$UPSTREAM_URL"
fi

RUNTIME_HEAD="$(git -C "$TARGET" rev-parse HEAD)"
if [[ "$RUNTIME_HEAD" != "$SOURCE_HEAD" ]]; then
  echo "Runtime HEAD mismatch: source=$SOURCE_HEAD runtime=$RUNTIME_HEAD" >&2
  exit 4
fi
if [[ -n "$(git -C "$TARGET" status --porcelain)" ]]; then
  echo "Runtime checkout is dirty after deployment" >&2
  git -C "$TARGET" status --short >&2
  exit 5
fi

printf 'VNCCS runtime synced\nsource=%s\ntarget=%s\ncommit=%s\n' "$SOURCE_ROOT" "$TARGET" "$SOURCE_HEAD"
