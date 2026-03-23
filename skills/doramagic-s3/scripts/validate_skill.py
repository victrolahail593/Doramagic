#!/usr/bin/env python3
import sys
import argparse
import re
from pathlib import Path

def validate_skill(skill_dir):
    skill_path = Path(skill_dir)
    skill_md = skill_path / "SKILL.md"
    provenance_md = skill_path / "PROVENANCE.md"
    limitations_md = skill_path / "LIMITATIONS.md"

    errors = []
    warnings = []

    if not skill_md.exists():
        errors.append("Missing SKILL.md")
    else:
        content = skill_md.read_text()
        if "---" not in content:
            errors.append("SKILL.md missing frontmatter")
        if not re.search(r"^# .+", content, re.MULTILINE):
            errors.append("SKILL.md missing main heading")
        if "WHY" not in content:
            warnings.append("SKILL.md might be missing WHY section")
        if "UNSAID" not in content:
            warnings.append("SKILL.md might be missing UNSAID section")

    if not provenance_md.exists():
        warnings.append("Missing PROVENANCE.md")
    else:
        content = provenance_md.read_text()
        if not re.search(r"https?://", content):
            warnings.append("PROVENANCE.md missing source URLs")
        # Check for card-based provenance
        if "Card ID:" not in content and "Card" not in content:
             warnings.append("PROVENANCE.md should trace back to specific Knowledge Cards.")

    if not limitations_md.exists():
        warnings.append("Missing LIMITATIONS.md")
    else:
        content = limitations_md.read_text()
        # Dark Trap checks
        dark_trap_keywords = ["Dark Trap", "Risk", "Over-engineering", "Exception Bias", "Deceptive"]
        has_dark_trap = any(kw.lower() in content.lower() for kw in dark_trap_keywords)
        if not has_dark_trap:
            warnings.append("LIMITATIONS.md should contain Dark Trap evaluation results.")

    # WHY reversibility check (can be in SKILL.md or LIMITATIONS.md)
    combined_content = (skill_md.read_text() if skill_md.exists() else "") + \
                       (limitations_md.read_text() if limitations_md.exists() else "") + \
                       (provenance_md.read_text() if provenance_md.exists() else "")
    
    if "WHY" not in combined_content.upper() or "Reconstruct" not in combined_content and "Evidence" not in combined_content:
        warnings.append("Did not find explicit evaluation of WHY Reversibility (e.g., 'WHY evidence sufficient' or 'WHY cannot be reliably reconstructed').")

    return errors, warnings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir", help="Path to the skill directory")
    args = parser.parse_args()

    errors, warnings = validate_skill(args.skill_dir)

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"- [ERROR] {e}")
    else:
        print("Validation PASSED (with warnings if any):")

    for w in warnings:
        print(f"- [WARN] {w}")

    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
