#!/usr/bin/env python3
"""
Soul Extractor: Extract deterministic facts from a repository.
Produces repo_facts.json — a whitelist used for fact-checking extracted claims.

Usage:
    python3 extract_repo_facts.py --repo-path <path> --output-dir <output_dir>

Output: <output_dir>/artifacts/repo_facts.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extract_cli_commands(repo_path):
    """Find CLI commands defined in the repo (setup.py, pyproject.toml, package.json, etc.)."""
    commands = set()

    # Python: setup.py / pyproject.toml console_scripts
    for fname in ["setup.py", "setup.cfg", "pyproject.toml"]:
        fpath = os.path.join(repo_path, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            # Find console_scripts block and extract only those entries
            # Matches: "cmd = module:func" or "cmd=module:func"
            cs_match = re.search(r'console_scripts\s*[=:]\s*\[([^\]]*)\]', text, re.DOTALL)
            if cs_match:
                section = cs_match.group(1)
                for m in re.finditer(r'"([\w][\w-]+)\s*=', section):
                    commands.add(m.group(1))
                for m in re.finditer(r"'([\w][\w-]+)\s*=", section):
                    commands.add(m.group(1))

    # Node: package.json bin / scripts
    pkg = os.path.join(repo_path, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg, encoding="utf-8") as f:
                data = json.load(f)
            for key in data.get("bin", {}).keys():
                commands.add(key)
            for key in data.get("scripts", {}).keys():
                commands.add(f"npm run {key}")
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Shell scripts in bin/ or scripts/
    for bindir in ["bin", "scripts"]:
        dirpath = os.path.join(repo_path, bindir)
        if os.path.isdir(dirpath):
            for f in os.listdir(dirpath):
                full_path = os.path.join(dirpath, f)
                if not f.startswith(".") and os.path.isfile(full_path):
                    commands.add(f)

    return sorted(commands)


def extract_skill_names(repo_path):
    """Find skill/plugin names from skills/, plugins/, .claude/skills/ directories."""
    skills = set()

    for skilldir in ["skills", "plugins", ".claude/skills", ".claude/plugins"]:
        dirpath = os.path.join(repo_path, skilldir)
        if not os.path.isdir(dirpath):
            continue
        for entry in os.listdir(dirpath):
            full = os.path.join(dirpath, entry)
            if os.path.isdir(full) and not entry.startswith("."):
                skills.add(entry)
            # Also check SKILL.md name field
            skill_md = os.path.join(full, "SKILL.md")
            if os.path.exists(skill_md):
                with open(skill_md, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                m = re.search(r"^name:\s*(.+)", text, re.MULTILINE)
                if m:
                    skills.add(m.group(1).strip())

    return sorted(skills)


def extract_file_paths(repo_path):
    """List all non-hidden files relative to repo root (for source ref validation)."""
    paths = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("node_modules", "__pycache__", ".git", "venv", ".venv", "dist", "build")]
        for f in files:
            if not f.startswith("."):
                rel = os.path.relpath(os.path.join(root, f), repo_path)
                paths.append(rel)
    return sorted(paths)


def extract_config_keys(repo_path):
    """Find configuration keys from .env.example, config files, README."""
    keys = set()

    for fname in [".env.example", ".env.sample", "config.example.yaml",
                  "config.example.yml", "config.example.json"]:
        fpath = os.path.join(repo_path, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            for m in re.finditer(r"^([A-Z][A-Z0-9_]{2,})\s*=", text, re.MULTILINE):
                keys.add(m.group(1))

    return sorted(keys)


def detect_frameworks(repo_path, files):
    """检测项目使用的框架。确定性，无 LLM。"""
    frameworks = []
    all_files_lower = " ".join(f.lower() for f in files)

    # Python frameworks
    req_files = ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"]
    has_python_deps = False
    deps_text = ""
    for rf in req_files:
        fpath = os.path.join(repo_path, rf)
        if os.path.exists(fpath):
            has_python_deps = True
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                deps_text += f.read().lower() + "\n"

    if has_python_deps:
        if "django" in deps_text or "manage.py" in all_files_lower:
            frameworks.append("Django")
        if "fastapi" in deps_text:
            frameworks.append("FastAPI")
        if "flask" in deps_text:
            frameworks.append("Flask")
        if "homeassistant" in deps_text or "home-assistant" in deps_text or "custom_components" in all_files_lower:
            frameworks.append("HomeAssistant")

    # JS frameworks
    pkg_path = os.path.join(repo_path, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                pkg_text = f.read().lower()
            if "react" in pkg_text:
                frameworks.append("React")
            if "\"next\"" in pkg_text or "\"next\"" in pkg_text:
                frameworks.append("Next.js")
            if "vue" in pkg_text:
                frameworks.append("Vue")
        except (json.JSONDecodeError, IOError):
            pass

    # Go
    if os.path.exists(os.path.join(repo_path, "go.mod")):
        frameworks.append("Go")

    # Rust
    if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
        frameworks.append("Rust")

    return sorted(set(frameworks))


def generate_project_narrative(repo_name, commands, skills, config_keys, files):
    """生成 50-100 词的确定性项目叙事摘要。无 LLM，纯模板。"""
    # 检测主语言
    ext_count = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in (".py", ".js", ".ts", ".go", ".rs", ".java", ".rb", ".php", ".swift", ".kt"):
            ext_count[ext] = ext_count.get(ext, 0) + 1
    primary_lang = ""
    if ext_count:
        top_ext = max(ext_count, key=ext_count.get)
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
            ".php": "PHP", ".swift": "Swift", ".kt": "Kotlin",
        }
        primary_lang = lang_map.get(top_ext, "")

    # 检测框架
    frameworks = []
    all_files_str = " ".join(files)
    if "requirements.txt" in all_files_str or "pyproject.toml" in all_files_str:
        if "django" in all_files_str.lower() or "manage.py" in all_files_str:
            frameworks.append("Django")
        if "fastapi" in all_files_str.lower():
            frameworks.append("FastAPI")
        if "flask" in all_files_str.lower():
            frameworks.append("Flask")
    if "package.json" in all_files_str:
        if "react" in all_files_str.lower() or "jsx" in all_files_str.lower():
            frameworks.append("React")
        if "next" in all_files_str.lower():
            frameworks.append("Next.js")
        if "vue" in all_files_str.lower():
            frameworks.append("Vue")
    if "go.mod" in all_files_str:
        frameworks.append("Go modules")
    if "Cargo.toml" in all_files_str:
        frameworks.append("Rust/Cargo")

    # 组装叙事
    parts = []
    parts.append(f"{repo_name} is a {primary_lang} project" if primary_lang else f"{repo_name} is a software project")

    if frameworks:
        parts[0] += f" using {', '.join(frameworks[:3])}"

    parts[0] += f" with {len(files)} source files."

    if commands:
        cmd_list = ", ".join(f"`{c}`" for c in commands[:5])
        parts.append(f"It provides CLI commands: {cmd_list}.")

    if skills:
        skill_list = ", ".join(skills[:3])
        parts.append(f"It includes skills/plugins: {skill_list}.")

    if config_keys:
        parts.append(f"It uses {len(config_keys)} configuration keys.")

    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Extract deterministic facts from a repo")
    parser.add_argument("--repo-path", required=True, help="Path to cloned repo")
    parser.add_argument("--output-dir", required=True, help="Output directory (artifacts/ will be used)")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.isdir(repo_path):
        print(f"ERROR: repo path not found: {repo_path}", file=sys.stderr)
        sys.exit(1)

    artifacts_dir = os.path.join(output_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    commands = extract_cli_commands(repo_path)
    skills = extract_skill_names(repo_path)
    files = extract_file_paths(repo_path)
    config_keys = extract_config_keys(repo_path)
    frameworks = detect_frameworks(repo_path, files)

    facts = {
        "repo_path": repo_path,
        "commands": commands,
        "skills": skills,
        "files": files,
        "config_keys": config_keys,
        "frameworks": frameworks,
        "project_narrative": generate_project_narrative(
            repo_name=os.path.basename(repo_path),
            commands=commands,
            skills=skills,
            config_keys=config_keys,
            files=files,
        ),
    }

    out_path = os.path.join(artifacts_dir, "repo_facts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, ensure_ascii=False)

    print(f"repo_facts={out_path}")
    print(f"  commands: {len(facts['commands'])}")
    print(f"  skills:   {len(facts['skills'])}")
    print(f"  files:    {len(facts['files'])}")
    print(f"  config_keys: {len(facts['config_keys'])}")


if __name__ == "__main__":
    main()
