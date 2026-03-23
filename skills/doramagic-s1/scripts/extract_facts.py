#!/usr/bin/env python3
"""extract_facts.py — 从本地仓库目录提取确定性事实，输出 facts.json。

设计原则：代码说事实，AI 说故事。
此脚本只做确定性提取，绝不调用 LLM。所有输出可重现。

用法：
    python3 extract_facts.py <repo_dir> --output facts.json
    python3 extract_facts.py /tmp/repos/myproject-main --output /tmp/facts.json

输出格式（facts.json）：
    {
        "repo_name": "myproject-main",
        "languages": ["Python", "JavaScript"],
        "frameworks": ["Django"],
        "entrypoints": ["manage.py"],
        "commands": ["python manage.py runserver", "pytest"],
        "storage_paths": ["data/"],
        "dependencies": ["django", "requests"],
        "repo_summary": "Repository 'myproject-main' written in Python. ...",
        "file_count": 42,
        "has_tests": true,
        "has_ci": true,
        "readme_excerpt": "First 500 chars of README...",
        "license": "MIT"
    }
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 语言检测规则
# ---------------------------------------------------------------------------

_EXT_TO_LANG: dict[str, str] = {
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
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".dart": "Dart",
    ".elm": "Elm",
    ".ex": "Elixir",
    ".exs": "Elixir",
}

# ---------------------------------------------------------------------------
# 框架检测
# ---------------------------------------------------------------------------

_FRAMEWORK_INDICATORS: list[tuple[str, str]] = [
    ("next.config.js", "Next.js"),
    ("next.config.ts", "Next.js"),
    ("next.config.mjs", "Next.js"),
    ("nuxt.config.ts", "Nuxt.js"),
    ("nuxt.config.js", "Nuxt.js"),
    ("vite.config.ts", "Vite"),
    ("vite.config.js", "Vite"),
    ("angular.json", "Angular"),
    ("svelte.config.js", "Svelte"),
    ("gatsby-config.js", "Gatsby"),
    ("astro.config.mjs", "Astro"),
    ("manage.py", "Django"),
    ("pyproject.toml", "_check_pyproject"),
    ("requirements.txt", "_check_requirements"),
    ("Cargo.toml", "Rust/Cargo"),
    ("go.mod", "Go module"),
    ("pom.xml", "Maven/Java"),
    ("build.gradle", "Gradle/Java"),
    ("mix.exs", "Elixir/Mix"),
    ("pubspec.yaml", "Flutter/Dart"),
]

_PYPROJECT_KEYWORDS: dict[str, str] = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "starlette": "Starlette",
    "litestar": "Litestar",
    "tornado": "Tornado",
    "streamlit": "Streamlit",
}

_REQUIREMENTS_KEYWORDS: dict[str, str] = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "starlette": "Starlette",
    "streamlit": "Streamlit",
    "sqlalchemy": "SQLAlchemy",
}

# ---------------------------------------------------------------------------
# 入口点候选
# ---------------------------------------------------------------------------

_ENTRYPOINT_CANDIDATES: list[str] = [
    "src/app/api/chat/route.ts",
    "src/app/layout.tsx",
    "src/pages/index.tsx",
    "src/pages/index.js",
    "pages/index.tsx",
    "pages/index.js",
    "src/index.ts",
    "src/index.js",
    "index.ts",
    "index.js",
    "server.ts",
    "server.js",
    "main.py",
    "app.py",
    "manage.py",
    "run.py",
    "src/main.py",
    "main.go",
    "cmd/main.go",
    "src/main.rs",
    "main.rs",
    "lib/main.dart",
]

_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage", ".tox",
    "vendor", "target", ".cargo",
}

# ---------------------------------------------------------------------------
# 检测函数
# ---------------------------------------------------------------------------


def _detect_languages(repo_path: Path) -> list[str]:
    lang_counts: dict[str, int] = {}
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            lang = _EXT_TO_LANG.get(ext)
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return [lang for lang, _ in sorted(lang_counts.items(), key=lambda x: -x[1])]


def _detect_frameworks(repo_path: Path) -> list[str]:
    frameworks: list[str] = []
    seen: set[str] = set()
    root_files = {f.name for f in repo_path.iterdir() if f.is_file()}

    for indicator, framework in _FRAMEWORK_INDICATORS:
        if indicator not in root_files:
            continue
        if framework == "_check_pyproject":
            try:
                content = (repo_path / "pyproject.toml").read_text(encoding="utf-8").lower()
                for keyword, fw in _PYPROJECT_KEYWORDS.items():
                    if keyword in content and fw not in seen:
                        frameworks.append(fw)
                        seen.add(fw)
            except OSError:
                pass
        elif framework == "_check_requirements":
            try:
                content = (repo_path / "requirements.txt").read_text(encoding="utf-8").lower()
                for keyword, fw in _REQUIREMENTS_KEYWORDS.items():
                    if keyword in content and fw not in seen:
                        frameworks.append(fw)
                        seen.add(fw)
            except OSError:
                pass
        else:
            if framework not in seen:
                frameworks.append(framework)
                seen.add(framework)
    return frameworks


def _detect_entrypoints(repo_path: Path) -> list[str]:
    return [c for c in _ENTRYPOINT_CANDIDATES if (repo_path / c).exists()]


def _detect_commands(repo_path: Path) -> list[str]:
    commands: list[str] = []

    pkg_json = repo_path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            for name in ["dev", "start", "build", "test", "lint"]:
                if name in data.get("scripts", {}):
                    commands.append(f"npm run {name}")
        except (OSError, ValueError):
            pass

    makefile = repo_path / "Makefile"
    if makefile.exists():
        try:
            for line in makefile.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line.endswith(":"):
                    target = line.rstrip(":")
                    if target and not target.startswith("."):
                        commands.append(f"make {target}")
        except OSError:
            pass

    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "[tool.pytest" in content:
                commands.append("pytest")
            if "ruff" in content:
                commands.append("ruff check .")
            if "mypy" in content:
                commands.append("mypy .")
        except OSError:
            pass

    manage_py = repo_path / "manage.py"
    if manage_py.exists():
        commands.extend(["python manage.py runserver", "python manage.py migrate"])

    return commands


def _detect_storage_paths(repo_path: Path) -> list[str]:
    candidates = ["data/", "storage/", "db/", "database/", "uploads/", "files/", "cache/", "static/", "media/"]
    return [c for c in candidates if (repo_path / c.rstrip("/")).exists()]


def _detect_dependencies(repo_path: Path) -> list[str]:
    deps: list[str] = []

    pkg_json = repo_path / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            for section in ["dependencies", "devDependencies"]:
                deps.extend(data.get(section, {}).keys())
        except (OSError, ValueError):
            pass

    requirements = repo_path / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    pkg = re.split(r"[><=![\s]", line)[0].strip()
                    if pkg:
                        deps.append(pkg)
        except OSError:
            pass

    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists() and not requirements.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # Extract dependencies from [project] section (simple heuristic)
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                elif in_deps:
                    line = line.strip()
                    if line.startswith('"') or line.startswith("'"):
                        pkg = re.split(r"[><=![\s\"']", line.strip("\"' "))[0].strip()
                        if pkg and pkg not in ("[", "]"):
                            deps.append(pkg)
                    elif not line or line.startswith("["):
                        in_deps = False
        except OSError:
            pass

    return list(dict.fromkeys(deps))  # deduplicate preserving order


def _detect_license(repo_path: Path) -> str:
    for name in ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"]:
        p = repo_path / name
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")[:500]
                for keyword in ["MIT", "Apache", "GPL", "BSD", "ISC", "MPL", "AGPL", "LGPL", "Unlicense", "CC0"]:
                    if keyword in content:
                        return keyword
                return "Unknown (license file present)"
            except OSError:
                pass
    return "No license file found"


def _detect_has_tests(repo_path: Path) -> bool:
    test_dirs = ["tests", "test", "__tests__", "spec", "specs"]
    for d in test_dirs:
        if (repo_path / d).is_dir():
            return True
    # Check for test files in root
    for pattern in ["test_*.py", "*_test.py", "*.test.ts", "*.spec.ts"]:
        import glob
        if glob.glob(str(repo_path / pattern)):
            return True
    return False


def _detect_has_ci(repo_path: Path) -> bool:
    ci_paths = [
        ".github/workflows",
        ".travis.yml",
        ".circleci/config.yml",
        "Jenkinsfile",
        ".gitlab-ci.yml",
        "bitbucket-pipelines.yml",
    ]
    return any((repo_path / p).exists() for p in ci_paths)


def _get_readme_excerpt(repo_path: Path, max_chars: int = 800) -> str:
    for name in ["README.md", "README.rst", "README.txt", "README"]:
        p = repo_path / name
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                return content[:max_chars]
            except OSError:
                pass
    return ""


def _count_files(repo_path: Path) -> int:
    count = 0
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        count += len(files)
    return count


# ---------------------------------------------------------------------------
# 公开入口
# ---------------------------------------------------------------------------


def extract_facts(repo_path: str) -> dict:
    """提取仓库确定性事实，返回 dict。"""
    path = Path(repo_path).resolve()
    if not path.exists():
        raise ValueError(f"repo_path does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"repo_path is not a directory: {path}")

    languages = _detect_languages(path)
    frameworks = _detect_frameworks(path)
    entrypoints = _detect_entrypoints(path)
    commands = _detect_commands(path)
    storage_paths = _detect_storage_paths(path)
    dependencies = _detect_dependencies(path)
    license_str = _detect_license(path)
    has_tests = _detect_has_tests(path)
    has_ci = _detect_has_ci(path)
    readme_excerpt = _get_readme_excerpt(path)
    file_count = _count_files(path)

    lang_str = ", ".join(languages[:3]) if languages else "unknown"
    summary_parts = [f"Repository '{path.name}' written in {lang_str}."]
    if frameworks:
        summary_parts.append(f"Detected frameworks: {', '.join(frameworks)}.")
    if entrypoints:
        summary_parts.append(f"Primary entrypoint: {entrypoints[0]}.")
    else:
        summary_parts.append("No standard entrypoint detected.")

    return {
        "schema_version": "dm.repo-facts.v1",
        "repo_name": path.name,
        "repo_path": str(path),
        "languages": languages,
        "frameworks": frameworks,
        "entrypoints": entrypoints,
        "commands": commands,
        "storage_paths": storage_paths,
        "dependencies": dependencies[:50],  # cap at 50
        "license": license_str,
        "has_tests": has_tests,
        "has_ci": has_ci,
        "file_count": file_count,
        "readme_excerpt": readme_excerpt,
        "repo_summary": " ".join(summary_parts),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Doramagic extract_facts — 从仓库目录提取确定性事实"
    )
    parser.add_argument("repo_dir", help="本地仓库目录路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    try:
        facts = extract_facts(args.repo_dir)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Facts extracted: {len(facts['languages'])} languages, {len(facts['frameworks'])} frameworks")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
