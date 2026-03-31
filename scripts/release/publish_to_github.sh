#!/bin/bash
set -euo pipefail

# ─── Doramagic: Publish to GitHub ────────────────────────────────
# 直接推送本地 main 分支到 GitHub（保留完整 commit 历史）。
# .gitignore 已排除所有内部文件，无需临时目录清理。
#
# Usage:
#   ./scripts/release/publish_to_github.sh v13.0.0
#   ./scripts/release/publish_to_github.sh v13.0.0 --dry-run
# ──────────────────────────────────────────────────────────────────

VERSION="${1:-}"
DRY_RUN=false
[[ "${2:-}" == "--dry-run" ]] && DRY_RUN=true

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version> [--dry-run]"
    echo "  e.g. $0 v13.0.0"
    exit 1
fi

# Validate semver format
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: Version must be semver format: vX.Y.Z (got: $VERSION)"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "═══════════════════════════════════════════"
echo "  Doramagic Release: $VERSION"
echo "═══════════════════════════════════════════"

# ─── Step 1: Pre-flight checks ───────────────────────────────────

echo ""
echo "▶ Step 1: Pre-flight checks"

# Must be on main branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" ]]; then
    echo "  ERROR: Must be on 'main' branch (currently on '$BRANCH')"
    exit 1
fi

# Working tree must be clean
if [[ -n "$(git status --porcelain)" ]]; then
    echo "  ERROR: Working tree is dirty. Commit or stash changes first."
    git status --short
    exit 1
fi

# Check github remote
GITHUB_URL=$(git remote get-url github 2>/dev/null || echo "")
if [[ -z "$GITHUB_URL" ]]; then
    echo "  ERROR: No 'github' remote configured. Add it with:"
    echo "    git remote add github https://github.com/tangweigang-jpg/Doramagic.git"
    exit 1
fi

echo "  ✓ On main branch, working tree clean"
echo "  ✓ GitHub remote: $GITHUB_URL"

# ─── Step 2: Run tests ───────────────────────────────────────────

echo ""
echo "▶ Step 2: Running tests"

if [[ -f "Makefile" ]] && grep -q "^test:" Makefile; then
    make test || { echo "  ERROR: Tests failed. Fix before releasing."; exit 1; }
    echo "  ✓ Tests passed"
else
    echo "  ⚠ No test target in Makefile, skipping"
fi

# ─── Step 2.5: Package self-contained skill ──────────────────────

echo ""
echo "▶ Step 2.5: Packaging self-contained skill"

PACKAGE_SCRIPT="$PROJECT_ROOT/scripts/release/package_skill.sh"
if [[ -x "$PACKAGE_SCRIPT" ]]; then
    bash "$PACKAGE_SCRIPT"
    echo "  ✓ Skill packaged"
    # Commit packaged skill if changed
    if [[ -n "$(git status --porcelain skills/doramagic/)" ]]; then
        git add skills/doramagic/
        git commit -q -m "chore: package self-contained skill for release"
        echo "  ✓ Packaged skill committed"
    fi
else
    echo "  ⚠ package_skill.sh not found, skipping"
fi

# ─── Step 3: Verify community standard files ─────────────────────

echo ""
echo "▶ Step 3: Checking community standard files"

REQUIRED_FILES=(
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "CONTRIBUTING.md"
    "SECURITY.md"
    "INSTALL.md"
    ".env.example"
    ".gitignore"
)

MISSING=0
for f in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "  ✓ $f"
    else
        echo "  ✗ MISSING: $f"
        MISSING=1
    fi
done

if [[ $MISSING -eq 1 ]]; then
    echo ""
    echo "  ERROR: Missing required community files. Add them before releasing."
    exit 1
fi

# ─── Step 4: Version stamp ───────────────────────────────────────

echo ""
echo "▶ Step 4: Version stamp"

TRACKED_COUNT=$(git ls-files | wc -l | tr -d ' ')
BRICK_COUNT=0
if [[ -d "bricks" ]]; then
    BRICK_COUNT=$(cat bricks/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
fi

echo "  Tracked files: $TRACKED_COUNT"
echo "  Bricks: $BRICK_COUNT"
echo "  Version: $VERSION"

# ─── Step 5: Dry-run check ──────────────────────────────────────

if $DRY_RUN; then
    echo ""
    echo "  [DRY RUN] Would push $TRACKED_COUNT tracked files as $VERSION to GitHub"
    echo "  [DRY RUN] .gitignore excludes: docs/, research/, experiments/, races/, TODOS.md, etc."
    echo ""
    echo "  Verify what GitHub will see:"
    echo "    git ls-files | head -30"
    exit 0
fi

# ─── Step 6: Tag and push to GitHub ──────────────────────────────

echo ""
echo "▶ Step 6: Push to GitHub (preserving commit history)"

# Tag locally
git tag "$VERSION" 2>/dev/null && echo "  ✓ Tagged $VERSION locally" || echo "  ⚠ Tag $VERSION already exists locally"

# Push main branch with full history
git push github main --force
echo "  ✓ Pushed main to GitHub (with full commit history)"

# Push tag
git push github "$VERSION" 2>/dev/null && echo "  ✓ Pushed tag $VERSION" || echo "  ⚠ Tag $VERSION already exists on GitHub"

# Fetch back to sync tracking ref
git fetch github
echo "  ✓ Synced github/main tracking ref"

# ─── Step 7: Tag in source repo (Gitea) ─────────────────────────

echo ""
echo "▶ Step 7: Tag in Gitea"
git push origin "$VERSION" 2>/dev/null && echo "  ✓ Pushed tag to Gitea" || echo "  ⚠ Could not push tag to Gitea"

# ─── Step 8: Publish to ClawHub ─────────────────────────────────

echo ""
echo "▶ Step 8: Publish to ClawHub"

SEMVER="${VERSION#v}"  # strip leading 'v' for clawhub (13.0.0 not v13.0.0)
SKILL_DIR="$PROJECT_ROOT/skills/doramagic"

if [[ ! -d "$SKILL_DIR" ]]; then
    echo "  ⚠ skills/doramagic not found, skipping ClawHub publish"
else
    if command -v npx &>/dev/null; then
        # 发布到两个 slug（历史原因：dora 和 doramagic 都有用户安装）
        for SLUG in dora doramagic; do
            echo "  Publishing ${SLUG}@$SEMVER to ClawHub..."
            npx clawhub@latest publish "$SKILL_DIR" \
                --slug "$SLUG" \
                --name "Doramagic" \
                --version "$SEMVER" \
                --changelog "Release $VERSION" \
                --tags latest 2>&1 | tail -1

            if [[ $? -eq 0 ]]; then
                echo "  ✓ Published ${SLUG}@$SEMVER"
            else
                echo "  ⚠ ${SLUG} publish failed (non-blocking)"
            fi
        done
        echo "  Note: skills may be hidden for a few minutes during security scan"
    else
        echo "  ⚠ npx not found, skipping ClawHub publish"
        echo "  Manual: npx clawhub@latest publish skills/doramagic --slug dora --version $SEMVER"
        echo "  Manual: npx clawhub@latest publish skills/doramagic --slug doramagic --version $SEMVER"
    fi
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ✓ Release $VERSION complete"
echo "  GitHub: https://github.com/tangweigang-jpg/Doramagic"
echo "  ClawHub: https://clawhub.ai/skills/dora"
echo "═══════════════════════════════════════════"
