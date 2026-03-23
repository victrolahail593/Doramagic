#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

# Language detection rules
_EXT_TO_LANG = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
    ".sh": "Shell",
}

def detect_languages(repo_path: Path):
    lang_counts = {}
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".nuxt", "coverage"}
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            lang = _EXT_TO_LANG.get(ext)
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return [lang for lang, _ in sorted(lang_counts.items(), key=lambda x: -x[1])]

def detect_frameworks(repo_path: Path):
    frameworks = []
    root_files = {f.name for f in repo_path.iterdir() if f.is_file()}
    if "package.json" in root_files:
        frameworks.append("Node.js")
    if "pyproject.toml" in root_files or "requirements.txt" in root_files:
        frameworks.append("Python")
    if "go.mod" in root_files:
        frameworks.append("Go")
    # Add more heuristics as needed
    return frameworks

def detect_entrypoints(repo_path: Path):
    candidates = ["main.py", "app.py", "index.ts", "index.js", "src/main.py", "src/index.ts"]
    return [c for c in candidates if (repo_path / c).exists()]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_dir", help="Path to the repository directory")
    parser.add_argument("--output", help="Path to the output JSON file", default="facts.json")
    args = parser.parse_args()

    repo_path = Path(args.repo_dir).resolve()
    if not repo_path.is_dir():
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    facts = {
        "repo_name": repo_path.name,
        "languages": detect_languages(repo_path),
        "frameworks": detect_frameworks(repo_path),
        "entrypoints": detect_entrypoints(repo_path),
        "structure": [str(p.relative_to(repo_path)) for p in repo_path.glob("*") if p.is_dir()][:10]
    }

    with open(args.output, "w") as f:
        json.dump(facts, f, indent=2)
    print(f"Facts extracted to {args.output}")

if __name__ == "__main__":
    main()
