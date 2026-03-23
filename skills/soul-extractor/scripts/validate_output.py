#!/usr/bin/env python3
"""
Doramagic v1.0: Output Validation
Validates the final CLAUDE.md for three-module structural compliance:
Soul (CRITICAL RULES + EXPERT KNOWLEDGE) + Architecture (MODULE MAP) + Community (COMMUNITY WISDOM).

Usage:
    python3 validate_output.py --file <path_to_CLAUDE.md>

Exit codes:
    0 = all checks pass
    1 = validation failures found
"""

import argparse
import re
import sys


def validate_output(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    total_len = len(content)
    errors = []
    metrics = {}

    # Check CRITICAL RULES section exists (Soul module)
    cr_match = re.search(r'^## CRITICAL RULES\b', content, re.MULTILINE)
    if not cr_match:
        errors.append("Missing '## CRITICAL RULES' section")
        metrics["critical_rules_section"] = False
    else:
        metrics["critical_rules_section"] = True

    # Check EXPERT KNOWLEDGE section exists (Soul module)
    ek_match = re.search(r'^## EXPERT KNOWLEDGE\b', content, re.MULTILINE)
    if not ek_match:
        errors.append("Missing '## EXPERT KNOWLEDGE' section")

    # Check QUICK REFERENCE section exists (Soul module)
    qr_match = re.search(r'^## QUICK REFERENCE\b', content, re.MULTILINE)
    if not qr_match:
        errors.append("Missing '## QUICK REFERENCE' section")

    # Check MODULE MAP section exists (Architecture module)
    mm_match = re.search(r'^## MODULE MAP\b', content, re.MULTILINE)
    if not mm_match:
        errors.append("Missing '## MODULE MAP' section (Stage M output not assembled)")
    else:
        # Check module map has actual module entries
        module_entries = re.findall(r'^### M-\d+', content, re.MULTILINE)
        metrics["module_count"] = len(module_entries)
        if len(module_entries) < 3:
            errors.append(f"MODULE MAP has only {len(module_entries)} module entries (minimum 3)")

    # Check COMMUNITY WISDOM section exists (Community module)
    cw_match = re.search(r'^## COMMUNITY WISDOM\b', content, re.MULTILINE)
    if not cw_match:
        errors.append("Missing '## COMMUNITY WISDOM' section (Stage C output not assembled)")
    else:
        # Check community wisdom has pain points
        pain_points = re.findall(r'^### 痛点', content, re.MULTILINE)
        metrics["pain_point_count"] = len(pain_points)
        if len(pain_points) < 2:
            errors.append(f"COMMUNITY WISDOM has only {len(pain_points)} pain points (minimum 2)")

    # Count CRITICAL rules
    critical_count = len(re.findall(r'\[CRITICAL\]', content))
    metrics["critical_count"] = critical_count

    # Count HIGH rules
    high_count = len(re.findall(r'\[HIGH\]', content))
    metrics["high_count"] = high_count

    # Total rules in CRITICAL RULES section
    total_rules = critical_count + high_count
    metrics["total_rules"] = total_rules
    if total_rules < 3:
        errors.append(f"Only {total_rules} rules in CRITICAL RULES section (minimum 3)")

    # Check CRITICAL RULES section proportion (must be at least 15% of file)
    if cr_match and ek_match:
        cr_section_len = ek_match.start() - cr_match.start()
        cr_proportion = cr_section_len / total_len if total_len > 0 else 0
        metrics["critical_rules_proportion"] = round(cr_proportion, 3)
        if cr_proportion < 0.15:
            errors.append(f"CRITICAL RULES section is {cr_proportion:.1%} of file (minimum 15%)")

    # Check rules have conditional language
    rule_lines = re.findall(r'\*\*\[(?:CRITICAL|HIGH)\]\*\*.*?—\s*(.*)', content)
    rules_with_condition = 0
    condition_patterns = [r'\bif\b', r'\bwhen\b', r'\bthen\b', r'\bmust\b',
                          r'\bnever\b', r'\bbefore\b', r'\bafter\b', r'\bunless\b']
    for rule_text in rule_lines:
        if any(re.search(p, rule_text, re.IGNORECASE) for p in condition_patterns):
            rules_with_condition += 1
    metrics["rules_with_condition"] = rules_with_condition

    # Print results
    print(f"Output validation: {filepath}")
    print(f"  File size: {total_len} bytes")
    print(f"  [Soul]         CRITICAL rules: {critical_count}, HIGH rules: {high_count}")
    if "critical_rules_proportion" in metrics:
        print(f"  [Soul]         Rules section proportion: {metrics['critical_rules_proportion']:.1%}")
    print(f"  [Soul]         Rules with conditions: {rules_with_condition}/{len(rule_lines)}")
    if "module_count" in metrics:
        print(f"  [Architecture] Modules identified: {metrics['module_count']}")
    if "pain_point_count" in metrics:
        print(f"  [Community]    Pain points documented: {metrics['pain_point_count']}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print(f"\nPASSED — all three modules assembled (Soul + Architecture + Community)")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validate Doramagic output")
    parser.add_argument("--file", required=True, help="Path to CLAUDE.md")
    args = parser.parse_args()

    if not validate_output(args.file):
        sys.exit(1)


if __name__ == "__main__":
    main()
