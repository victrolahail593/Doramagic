#!/bin/bash
# Soul Extractor: Prepare repository for extraction
# Usage: bash prepare-repo.sh <repo_url_or_path> [output_dir]
set -euo pipefail
export PATH="$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

REPO_INPUT="${1:?Usage: prepare-repo.sh <repo_url_or_path> [output_dir]}"
REPO_NAME=$(basename "$REPO_INPUT" .git)
OUTPUT_DIR="${2:-$HOME/soul-output/$REPO_NAME}"

# GitHub mirror list for China mainland users
GITHUB_MIRRORS=(
    ""  # try original URL first
    "https://ghproxy.net/"
    "https://mirror.ghproxy.com/"
    "https://gh-proxy.com/"
)

# Create dirs
mkdir -p "$OUTPUT_DIR"/{artifacts,soul/cards/{concepts,workflows,rules}}

# Clone if URL
if [[ "$REPO_INPUT" == http* ]] || [[ "$REPO_INPUT" == git@* ]]; then
    CLONE_DIR="$OUTPUT_DIR/artifacts/_repo"
    if [ ! -d "$CLONE_DIR" ]; then
        CLONED=false
        for MIRROR in "${GITHUB_MIRRORS[@]}"; do
            if [[ -n "$MIRROR" ]] && [[ "$REPO_INPUT" == https://github.com/* ]]; then
                CLONE_URL="${MIRROR}${REPO_INPUT}"
                echo "Trying mirror: $CLONE_URL"
            else
                CLONE_URL="$REPO_INPUT"
                echo "Cloning: $CLONE_URL"
            fi
            if git clone --depth 1 "$CLONE_URL" "$CLONE_DIR" 2>&1; then
                CLONED=true
                echo "Clone succeeded via: $CLONE_URL"
                break
            else
                echo "Clone failed, trying next mirror..."
                rm -rf "$CLONE_DIR" 2>/dev/null || true
            fi
        done
        if [ "$CLONED" = false ]; then
            echo "ERROR: All clone attempts failed. Please provide a mirror URL or local path."
            exit 1
        fi
    fi
    REPO_PATH="$CLONE_DIR"
else
    REPO_PATH="$REPO_INPUT"
fi

# Repomix
cd "$REPO_PATH"
COMP="$OUTPUT_DIR/artifacts/packed_compressed.xml"
FULL="$OUTPUT_DIR/artifacts/packed_full.xml"
[ ! -f "$COMP" ] && npx repomix --compress --style xml -o "$COMP" 2>&1
[ ! -f "$FULL" ] && npx repomix --style xml -o "$FULL" 2>&1

# --- Collect community signals ---
# Uses dedicated Python script for proper scoring, dedup, and budget control
COMMUNITY="$OUTPUT_DIR/artifacts/community_signals.md"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$COMMUNITY" ]; then
    python3 "$SCRIPT_DIR/collect-community-signals.py" \
        --repo-url "$REPO_INPUT" \
        --repo-path "$REPO_PATH" \
        --output "$COMMUNITY" \
        2>&1 || echo "  [warn] Community signal collection failed, continuing without it"
fi
COMMUNITY_SIZE=$(wc -c < "$COMMUNITY" 2>/dev/null | tr -d ' ' || echo "0")

# --- Extract repo facts (for fact-checking in Stage 3.5) ---
REPO_FACTS="$OUTPUT_DIR/artifacts/repo_facts.json"
if [ ! -f "$REPO_FACTS" ]; then
    python3 "$SCRIPT_DIR/extract_repo_facts.py" \
        --repo-path "$REPO_PATH" \
        --output-dir "$OUTPUT_DIR" \
        2>&1 || echo "  [warn] Repo facts extraction failed, continuing without it"
fi
FACTS_SIZE=$(wc -c < "$REPO_FACTS" 2>/dev/null | tr -d ' ' || echo "0")

# Stats
echo ""
echo "READY"
echo "repo=$REPO_NAME"
echo "output=$OUTPUT_DIR"
echo "compressed=$COMP ($(wc -c < "$COMP" | tr -d ' ') bytes)"
echo "full=$FULL ($(wc -c < "$FULL" | tr -d ' ') bytes)"
echo "community=$COMMUNITY ($COMMUNITY_SIZE bytes)"
echo "facts=$REPO_FACTS ($FACTS_SIZE bytes)"
