#!/usr/bin/env python3
"""assemble_output.py — 把 SKILL.md + PROVENANCE.md + LIMITATIONS.md 写到指定输出目录。

支持两种输入模式：
1. 直接传内容字符串（--skill / --provenance / --limitations）
2. 从草稿文件读取内容（--skill-content-file / --provenance-content-file / --limitations-content-file）

用法：
    # 模式1：直接传内容
    python3 assemble_output.py \\
        --skill "# My Skill\\n..." \\
        --provenance "# PROVENANCE\\n..." \\
        --limitations "# LIMITATIONS\\n..." \\
        --output-dir /tmp/output/

    # 模式2：从文件读取内容
    python3 assemble_output.py \\
        --skill-content-file /tmp/skill_draft.md \\
        --provenance-content-file /tmp/provenance_draft.md \\
        --limitations-content-file /tmp/limitations_draft.md \\
        --output-dir /tmp/output/

输出：
    {output_dir}/SKILL.md
    {output_dir}/PROVENANCE.md
    {output_dir}/LIMITATIONS.md
    {output_dir}/manifest.json  (组装元数据)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# 组装逻辑
# ---------------------------------------------------------------------------


def _read_content(content_str: str | None, content_file: str | None, field_name: str) -> str:
    """从字符串或文件读取内容，两者都没有则报错。"""
    if content_str is not None:
        return content_str
    if content_file is not None:
        p = Path(content_file)
        if not p.exists():
            raise ValueError(f"Content file not found for {field_name}: {content_file}")
        return p.read_text(encoding="utf-8")
    raise ValueError(f"Must provide either --{field_name} or --{field_name}-content-file")


def _validate_content(content: str, field_name: str) -> list[str]:
    """基本内容检查，返回警告列表（不阻断写入）。"""
    warnings = []
    if len(content.strip()) < 50:
        warnings.append(f"{field_name} content is very short ({len(content.strip())} chars)")
    if field_name == "SKILL.md" and "---" not in content[:200]:
        warnings.append("SKILL.md appears to be missing YAML frontmatter (no '---' in first 200 chars)")
    if field_name == "PROVENANCE.md" and "https://" not in content:
        warnings.append("PROVENANCE.md contains no https:// URLs — traceability may fail validation")
    if field_name == "LIMITATIONS.md" and len(content.strip()) < 100:
        warnings.append("LIMITATIONS.md is very short — consider adding more limitation details")
    return warnings


def assemble_output(
    skill_content: str,
    provenance_content: str,
    limitations_content: str,
    output_dir: str,
) -> dict:
    """
    写入三份文件到 output_dir，返回组装清单 dict。
    """
    out = Path(output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    assembled_at = datetime.utcnow().isoformat() + "Z"
    warnings: list[str] = []
    files_written: list[str] = []

    # Validate content
    for content, name in [
        (skill_content, "SKILL.md"),
        (provenance_content, "PROVENANCE.md"),
        (limitations_content, "LIMITATIONS.md"),
    ]:
        warnings.extend(_validate_content(content, name))

    # Write files
    files_to_write = [
        ("SKILL.md", skill_content),
        ("PROVENANCE.md", provenance_content),
        ("LIMITATIONS.md", limitations_content),
    ]

    for filename, content in files_to_write:
        dest = out / filename
        # Ensure content ends with newline
        if content and not content.endswith("\n"):
            content += "\n"
        dest.write_text(content, encoding="utf-8")
        files_written.append(str(dest))

    # Write manifest
    manifest = {
        "schema_version": "dm.assembly-manifest.v1",
        "assembled_at": assembled_at,
        "output_dir": str(out),
        "files": files_written,
        "warnings": warnings,
        "status": "ok",
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Doramagic assemble_output — 组装 Skill bundle 到输出目录"
    )

    # Content input options (mode 1: direct string)
    parser.add_argument("--skill", type=str, default=None, help="SKILL.md 内容字符串")
    parser.add_argument("--provenance", type=str, default=None, help="PROVENANCE.md 内容字符串")
    parser.add_argument("--limitations", type=str, default=None, help="LIMITATIONS.md 内容字符串")

    # Content input options (mode 2: file path)
    parser.add_argument("--skill-content-file", type=str, default=None, help="SKILL.md 草稿文件路径")
    parser.add_argument("--provenance-content-file", type=str, default=None, help="PROVENANCE.md 草稿文件路径")
    parser.add_argument("--limitations-content-file", type=str, default=None, help="LIMITATIONS.md 草稿文件路径")

    parser.add_argument("--output-dir", required=True, help="输出目录（会自动创建）")

    args = parser.parse_args()

    # Resolve content
    try:
        skill_content = _read_content(args.skill, args.skill_content_file, "skill")
        provenance_content = _read_content(args.provenance, args.provenance_content_file, "provenance")
        limitations_content = _read_content(args.limitations, args.limitations_content_file, "limitations")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        manifest = assemble_output(skill_content, provenance_content, limitations_content, args.output_dir)
    except Exception as e:
        print(f"ERROR assembling output: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Assembly complete: {len(manifest['files'])} files written to {manifest['output_dir']}")
    for f in manifest["files"]:
        print(f"  - {f}")
    if manifest["warnings"]:
        print("\nWarnings:")
        for w in manifest["warnings"]:
            print(f"  ! {w}")
    print(f"\nManifest: {manifest['output_dir']}/manifest.json")


if __name__ == "__main__":
    main()
