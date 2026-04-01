# Doramagic Release Flow

Complete process. Do not skip any step.

```bash
# 1. Version sync (pyproject.toml + SKILL.md + SKILL-dora-extract.md + plugin.json)
#    - Update version in all 4 files
#    - Update git tag in SKILL.md install URL (@vX.Y.Z)
# 2. make check must pass
# 3. uv build --wheel (verify pip package builds cleanly)
bash scripts/publish_preflight.sh                            # 4. Preflight
bash scripts/release/publish_to_github.sh vX.Y.Z --dry-run   # 5. Dry run
bash scripts/release/publish_to_github.sh vX.Y.Z             # 6. Publish (GitHub + ClawHub)
# 7. Create GitHub Release (English release notes)
# 8. Write dev log + update pitfalls
```

- ClawHub slug: `dora` (not doramagic)
- GitHub remote: `https://github.com/tangweigang-jpg/Doramagic.git`
- Scripts auto-handle: GitHub push + tag + ClawHub publish

## Post-pip-package notes (v13.1.0+)

- **No more rsync**: `skills/doramagic/packages/` no longer exists. Python code is
  distributed via `pip install doramagic` (declared in SKILL.md `metadata.openclaw.install`).
- **Knowledge in pip package**: `knowledge/` is bundled as package_data in the wheel.
  Knowledge updates require a new pip package version.
- **Version tag matters**: The `@vX.Y.Z` in SKILL.md install URL must match the git tag.
  Users get the code from this exact tag.
