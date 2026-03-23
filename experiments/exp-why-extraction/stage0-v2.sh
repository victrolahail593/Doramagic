#!/bin/bash
# Stage 0 v2: 四层漏斗智能采样
# 改进点:
#   1. 自动检测项目类型（代码密集 vs 非代码/资源型）
#   2. Layer 1: 结构性文件（必选）
#   3. Layer 2: Import 依赖中心度
#   4. Layer 3: Git 变更热点
#   5. Layer 4: AST 语义块提取（替代"前150行"）
#   6. 非代码项目的特殊处理（README 深度分析 + 数据目录组织分析）
#
# 用法: ./stage0-v2.sh <project_dir> <output_file>

# Intentionally no set -e/-u/-o pipefail: many shell pipes return non-zero legitimately

PROJECT_DIR="$1"
OUTPUT_FILE="$2"

if [ -z "$PROJECT_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <project_dir> <output_file>"
    exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_DIR")
echo "=== Stage 0 v2: 智能采样 $PROJECT_NAME ===" >&2

# =============================================
# 辅助函数
# =============================================
strip_project_dir() {
    sed "s|$PROJECT_DIR/||; s|$PROJECT_DIR||"
}

# =============================================
# 项目类型检测
# =============================================
CODE_EXTENSIONS="py js ts tsx jsx go java rs rb c cpp h hpp cs swift kt"
CODE_FILE_COUNT=0
for ext in $CODE_EXTENSIONS; do
    count=$(find "$PROJECT_DIR" -type f -name "*.$ext" -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" 2>/dev/null | wc -l | tr -d ' ')
    CODE_FILE_COUNT=$((CODE_FILE_COUNT + count))
done

TOTAL_FILE_COUNT=$(find "$PROJECT_DIR" -type f -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')

echo "  检测到 $CODE_FILE_COUNT 个代码文件（共 $TOTAL_FILE_COUNT 个文件）" >&2

# 代码文件占比 < 10% 或 < 5 个 → 非代码项目
if [ "$CODE_FILE_COUNT" -lt 5 ]; then
    PROJECT_TYPE="non-code"
    echo "  项目类型: 非代码/资源型（代码文件 < 5）" >&2
else
    PROJECT_TYPE="code"
    echo "  项目类型: 代码密集型" >&2
fi

# =============================================
# 开始输出
# =============================================
echo "# repo_facts: $PROJECT_NAME" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## 项目类型: $PROJECT_TYPE" >> "$OUTPUT_FILE"
echo "代码文件: $CODE_FILE_COUNT / $TOTAL_FILE_COUNT" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# =============================================
# Layer 0: 基础信息（所有项目通用）
# =============================================
echo "## 文件类型分布" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -type f -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \
    | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15 >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## 目录结构（前三层）" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -maxdepth 3 -type d -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" \
    | strip_project_dir | sort | head -60 >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# =============================================
# Layer 1: 结构性文件（必选）
# =============================================
echo "## Layer 1: 结构性文件" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# README（完整，不截断——这是项目最重要的文档）
for readme in README.md README.rst README.txt README; do
    if [ -f "$PROJECT_DIR/$readme" ]; then
        README_LINES=$(wc -l < "$PROJECT_DIR/$readme" | tr -d ' ')
        echo "### $readme ($README_LINES 行)" >> "$OUTPUT_FILE"
        if [ "$README_LINES" -le 300 ]; then
            cat "$PROJECT_DIR/$readme" >> "$OUTPUT_FILE"
        else
            # 大型 README: 前 200 行 + 后 50 行 + 结构分析
            echo "#### 前 200 行" >> "$OUTPUT_FILE"
            head -200 "$PROJECT_DIR/$readme" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "#### 后 50 行" >> "$OUTPUT_FILE"
            tail -50 "$PROJECT_DIR/$readme" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "#### README 结构分析（所有标题）" >> "$OUTPUT_FILE"
            grep -n "^#" "$PROJECT_DIR/$readme" >> "$OUTPUT_FILE" 2>/dev/null || true
            echo "" >> "$OUTPUT_FILE"
            echo "#### README 链接统计" >> "$OUTPUT_FILE"
            echo "外部链接数: $(grep -oE 'https?://[^ )]+' "$PROJECT_DIR/$readme" 2>/dev/null | wc -l | tr -d ' ')" >> "$OUTPUT_FILE"
            echo "GitHub 链接数: $(grep -oE 'https?://github\.com/[^ )]+' "$PROJECT_DIR/$readme" 2>/dev/null | wc -l | tr -d ' ')" >> "$OUTPUT_FILE"
            echo "图片引用数: $(grep -cE '!\[' "$PROJECT_DIR/$readme" 2>/dev/null || echo 0)" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
        break
    fi
done

# 依赖文件（完整）
echo "### 依赖文件" >> "$OUTPUT_FILE"
DEP_FILES_FOUND=0
for dep_file in requirements.txt setup.py setup.cfg pyproject.toml package.json Cargo.toml go.mod Gemfile build.gradle pom.xml; do
    if [ -f "$PROJECT_DIR/$dep_file" ]; then
        echo "#### $dep_file" >> "$OUTPUT_FILE"
        cat "$PROJECT_DIR/$dep_file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        DEP_FILES_FOUND=$((DEP_FILES_FOUND + 1))
    fi
done
if [ "$DEP_FILES_FOUND" -eq 0 ]; then
    echo "(无依赖文件)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# CI/CD 配置
echo "### CI/CD 配置" >> "$OUTPUT_FILE"
CI_FOUND=0
for ci_dir in .github/workflows .gitlab-ci.yml .circleci .travis.yml; do
    if [ -d "$PROJECT_DIR/$ci_dir" ]; then
        for f in "$PROJECT_DIR/$ci_dir"/*.yml "$PROJECT_DIR/$ci_dir"/*.yaml; do
            if [ -f "$f" ]; then
                echo "#### $(echo "$f" | strip_project_dir)" >> "$OUTPUT_FILE"
                head -80 "$f" >> "$OUTPUT_FILE"
                echo "" >> "$OUTPUT_FILE"
                CI_FOUND=$((CI_FOUND + 1))
            fi
        done
    elif [ -f "$PROJECT_DIR/$ci_dir" ]; then
        echo "#### $ci_dir" >> "$OUTPUT_FILE"
        head -80 "$PROJECT_DIR/$ci_dir" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        CI_FOUND=$((CI_FOUND + 1))
    fi
done
if [ "$CI_FOUND" -eq 0 ]; then
    echo "(无 CI/CD 配置)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Docker / 部署配置
echo "### 容器与部署配置" >> "$OUTPUT_FILE"
DEPLOY_FOUND=0
for deploy_file in Dockerfile docker-compose.yml docker-compose.yaml Makefile Procfile; do
    if [ -f "$PROJECT_DIR/$deploy_file" ]; then
        echo "#### $deploy_file" >> "$OUTPUT_FILE"
        head -80 "$PROJECT_DIR/$deploy_file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        DEPLOY_FOUND=$((DEPLOY_FOUND + 1))
    fi
done
if [ "$DEPLOY_FOUND" -eq 0 ]; then
    echo "(无容器/部署配置)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# .github 其他文件 (FUNDING.yml, ISSUE_TEMPLATE 等)
echo "### .github 目录" >> "$OUTPUT_FILE"
if [ -d "$PROJECT_DIR/.github" ]; then
    find "$PROJECT_DIR/.github" -type f -not -path "*/workflows/*" 2>/dev/null | while read f; do
        echo "#### $(echo "$f" | strip_project_dir)" >> "$OUTPUT_FILE"
        head -30 "$f" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    done
else
    echo "(无 .github 目录)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# =============================================
# 分支: 代码密集型 vs 非代码型
# =============================================
if [ "$PROJECT_TYPE" = "code" ]; then

    # =============================================
    # Layer 2: Import 依赖中心度（仅代码项目）
    # =============================================
    echo "## Layer 2: Import 依赖中心度" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # 检测主要语言
    MAIN_LANG=$(find "$PROJECT_DIR" -type f -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" \
        \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.java" -o -name "*.rs" \) \
        | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')

    echo "主要语言: $MAIN_LANG" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ "$MAIN_LANG" = "py" ]; then
        # Python: 提取 import 关系，计算被引用次数
        echo "### 被引用最多的模块（Top 10）" >> "$OUTPUT_FILE"
        find "$PROJECT_DIR" -type f -name "*.py" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" \
            -exec grep -hE "^(from|import) " {} \; 2>/dev/null \
            | sed -E 's/^from ([^ ]+) import.*/\1/; s/^import ([^ ,]+).*/\1/' \
            | sed 's/\..*//' \
            | sort | uniq -c | sort -rn | head -10 >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"

        # 项目内部模块引用（排除标准库和第三方）
        echo "### 项目内部模块被引用次数（Top 10）" >> "$OUTPUT_FILE"
        PROJECT_PKG=$(find "$PROJECT_DIR" -maxdepth 2 -name "__init__.py" -not -path "*/venv/*" -not -path "*/.git/*" 2>/dev/null | head -1 | xargs -I{} dirname {} | xargs basename 2>/dev/null || echo "")
        if [ -n "$PROJECT_PKG" ]; then
            find "$PROJECT_DIR" -type f -name "*.py" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" \
                -exec grep -hE "^from ${PROJECT_PKG}\." {} \; 2>/dev/null \
                | sed -E "s/^from (${PROJECT_PKG}\.[^ ]+) import.*/\1/" \
                | sort | uniq -c | sort -rn | head -10 >> "$OUTPUT_FILE"
        else
            echo "(无法确定项目包名)" >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"

        # 找到被引用最多的文件，加入待采样列表
        echo "### 依赖中心度最高的文件（Top 5）" >> "$OUTPUT_FILE"
        if [ -n "$PROJECT_PKG" ]; then
            # 将模块路径转为文件路径
            find "$PROJECT_DIR" -type f -name "*.py" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" \
                -exec grep -lE "^from ${PROJECT_PKG}\." {} \; 2>/dev/null \
                | while read f; do
                    grep -hE "^from ${PROJECT_PKG}\." "$f" 2>/dev/null
                done \
                | sed -E "s/^from (${PROJECT_PKG}\.[^ ]+) import.*/\1/" \
                | sed "s|\.|/|g" \
                | sort | uniq -c | sort -rn | head -5 \
                | awk '{print $2}' \
                | while read mod_path; do
                    # 尝试 .py 和 __init__.py
                    for candidate in "$PROJECT_DIR/${mod_path}.py" "$PROJECT_DIR/${mod_path}/__init__.py"; do
                        if [ -f "$candidate" ]; then
                            echo "$candidate" | strip_project_dir
                            break
                        fi
                    done
                done >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    fi

    # =============================================
    # Layer 3: Git 变更热点（仅代码项目）
    # =============================================
    echo "## Layer 3: Git 变更热点" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ -d "$PROJECT_DIR/.git" ]; then
        COMMIT_COUNT=$(cd "$PROJECT_DIR" && git log --oneline 2>/dev/null | wc -l | tr -d ' ')
        echo "总提交数: $COMMIT_COUNT" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"

        if [ "$COMMIT_COUNT" -gt 1 ]; then
            echo "### 变更最频繁的文件（Top 10）" >> "$OUTPUT_FILE"
            cd "$PROJECT_DIR" && git log --name-only --pretty=format: --diff-filter=M 2>/dev/null \
                | grep -E "\.(py|js|ts|go|java|rs)$" \
                | sort | uniq -c | sort -rn | head -10 >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"

            echo "### 关键 commit messages（含设计决策关键词）" >> "$OUTPUT_FILE"
            cd "$PROJECT_DIR" && git log --oneline 2>/dev/null \
                | grep -iE "refactor|redesign|change.*to|replace|migrate|add support|breaking|rework|rewrite|simplif|optimi" \
                | head -15 >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    else
        echo "(非 Git 仓库)" >> "$OUTPUT_FILE"
    fi

    # =============================================
    # Layer 4: 智能代码采样
    # =============================================
    echo "## Layer 4: 关键代码片段" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # 收集候选文件: 合并 Layer 2 (中心度) + Layer 3 (热点) + 入口文件 + 最大文件
    CANDIDATES=$(mktemp)

    # 入口文件
    for entry in main.py app.py run.py manage.py __main__.py server.py cli.py; do
        find "$PROJECT_DIR" -maxdepth 3 -name "$entry" -not -path "*/.git/*" -not -path "*/venv/*" 2>/dev/null >> "$CANDIDATES"
    done

    # 抽象基类 / 接口文件
    find "$PROJECT_DIR" -type f -name "*.py" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" \
        -exec grep -lE "(ABC|abstractmethod|Protocol)" {} \; 2>/dev/null | head -5 >> "$CANDIDATES"

    # 核心目录（engine, core, base）
    for dir_pattern in engine core base; do
        find "$PROJECT_DIR" -type f -name "*.py" -path "*/${dir_pattern}/*" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null | head -3 >> "$CANDIDATES"
    done

    # 最大文件（兜底）
    find "$PROJECT_DIR" -type f -name "*.py" -not -name "__init__.py" -not -name "setup.py" \
        -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" -not -path "*/migrations/*" \
        -exec wc -l {} \; 2>/dev/null | sort -rn | head -5 | awk '{print $2}' >> "$CANDIDATES"

    # 去重并取 Top 8
    UNIQUE_FILES=$(sort -u "$CANDIDATES" | head -8)
    rm -f "$CANDIDATES"

    for f in $UNIQUE_FILES; do
        RELPATH=$(echo "$f" | strip_project_dir)
        FILE_LINES=$(wc -l < "$f" | tr -d ' ')
        echo "### $RELPATH ($FILE_LINES 行)" >> "$OUTPUT_FILE"

        # 尝试 AST 提取（Python 文件）
        if echo "$f" | grep -qE "\.py$"; then
            echo '```python' >> "$OUTPUT_FILE"

            # AST 提取: 类/函数签名 + docstring + 前 N 行实现
            python3 -c "
import ast, sys

try:
    with open('$f', 'r', encoding='utf-8', errors='replace') as fh:
        source = fh.read()
    tree = ast.parse(source)
    lines = source.splitlines()

    # 收集所有顶层定义
    defs = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, 'end_lineno', node.lineno + 30)
            defs.append((node.lineno, end_line, type(node).__name__, node.name))

    if not defs:
        # 没有类/函数定义，输出前 150 行
        for line in lines[:150]:
            print(line)
    else:
        # 输出 import 块
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from'):
                break
            if stripped.startswith('import') or stripped.startswith('from'):
                print(line)
        print()

        # 输出每个定义（优先级：类 > 函数）
        budget = 400  # 总行数预算
        used = 0
        for start, end, kind, name in defs:
            block_len = end - start + 1
            if block_len > 80:
                # 大块：取前 40 行 + 后 10 行
                for line in lines[start-1:start+39]:
                    print(line)
                print(f'    # ... ({block_len - 50} lines omitted) ...')
                for line in lines[end-10:end]:
                    print(line)
                used += 52
            else:
                for line in lines[start-1:end]:
                    print(line)
                used += block_len
            print()
            if used >= budget:
                remaining = len(defs) - defs.index((start, end, kind, name)) - 1
                if remaining > 0:
                    print(f'# ... {remaining} more definitions omitted ...')
                break
except Exception as e:
    # AST 解析失败，fallback 到前 200 行
    with open('$f', 'r', encoding='utf-8', errors='replace') as fh:
        for i, line in enumerate(fh):
            if i >= 200:
                break
            print(line, end='')
" >> "$OUTPUT_FILE" 2>/dev/null

            echo '```' >> "$OUTPUT_FILE"
        else
            # 非 Python 文件：前 200 行
            echo '```' >> "$OUTPUT_FILE"
            head -200 "$f" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
        fi
        echo "" >> "$OUTPUT_FILE"
    done

else
    # =============================================
    # 非代码项目: 特殊处理
    # =============================================
    echo "## 非代码项目分析" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # 数据目录深度分析
    echo "### 数据目录结构（完整）" >> "$OUTPUT_FILE"
    find "$PROJECT_DIR" -maxdepth 4 -type d -not -path "*/.git/*" \
        | strip_project_dir | sort >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    echo "### 数据文件列表（完整）" >> "$OUTPUT_FILE"
    find "$PROJECT_DIR" -type f -not -path "*/.git/*" -not -name ".DS_Store" -not -name "*.pyc" \
        | strip_project_dir | sort >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # 每种数据文件的样本
    echo "### 数据文件样本" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # 每个子目录随机取一个文件的前 20 行
    find "$PROJECT_DIR" -maxdepth 2 -type d -not -path "*/.git/*" -not -path "$PROJECT_DIR" | sort | while read dir; do
        SAMPLE=$(find "$dir" -maxdepth 1 -type f \( -name "*.txt" -o -name "*.json" -o -name "*.csv" -o -name "*.md" \) -not -name ".DS_Store" 2>/dev/null | head -1)
        if [ -n "$SAMPLE" ]; then
            SAMPLE_LINES=$(wc -l < "$SAMPLE" 2>/dev/null | tr -d ' ')
            echo "#### $(echo "$SAMPLE" | strip_project_dir) ($SAMPLE_LINES 行)" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            head -20 "$SAMPLE" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        fi
    done

    # 数据格式多样性分析
    echo "### 数据格式分析" >> "$OUTPUT_FILE"
    echo "不同目录的文件格式:" >> "$OUTPUT_FILE"
    find "$PROJECT_DIR" -maxdepth 2 -type d -not -path "*/.git/*" -not -path "$PROJECT_DIR" | sort | while read dir; do
        dirname=$(echo "$dir" | strip_project_dir)
        formats=$(find "$dir" -maxdepth 1 -type f -not -name ".DS_Store" 2>/dev/null | sed 's/.*\.//' | sort -u | tr '\n' ', ')
        count=$(find "$dir" -maxdepth 1 -type f -not -name ".DS_Store" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt 0 ]; then
            echo "  $dirname: $count 文件, 格式: $formats" >> "$OUTPUT_FILE"
        fi
    done
    echo "" >> "$OUTPUT_FILE"

    # 所有代码文件（即使很少也完整输出）
    if [ "$CODE_FILE_COUNT" -gt 0 ]; then
        echo "### 所有代码文件（完整）" >> "$OUTPUT_FILE"
        find "$PROJECT_DIR" -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.sh" \) -not -path "*/.git/*" -not -path "*/__pycache__/*" | sort | while read f; do
            echo "#### $(echo "$f" | strip_project_dir)" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            cat "$f" >> "$OUTPUT_FILE"
            echo '```' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        done
    fi

    # Git 信息（如果有）
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo "### Git 历史" >> "$OUTPUT_FILE"
        COMMIT_COUNT=$(cd "$PROJECT_DIR" && git log --oneline 2>/dev/null | wc -l | tr -d ' ')
        echo "总提交数: $COMMIT_COUNT" >> "$OUTPUT_FILE"
        cd "$PROJECT_DIR" && git log --oneline 2>/dev/null | head -20 >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
fi

# =============================================
# 配置文件内容（所有项目通用）
# =============================================
echo "## 配置文件内容" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -maxdepth 2 -type f \( -name "*.cfg" -o -name "*.ini" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" \) \
    -not -path "*/.git/*" -not -path "*/node_modules/*" -not -name "package-lock.json" -not -name "yarn.lock" \
    2>/dev/null | sort | while read f; do
        echo "### $(echo "$f" | strip_project_dir)" >> "$OUTPUT_FILE"
        head -50 "$f" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
done
echo "" >> "$OUTPUT_FILE"

# 输出统计
OUTPUT_LINES=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
echo "=== Stage 0 v2 完成: $OUTPUT_FILE ($OUTPUT_LINES 行) ===" >&2
