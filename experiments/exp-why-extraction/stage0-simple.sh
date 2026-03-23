#!/bin/bash
# 简化版 Stage 0：确定性提取基本项目信息
# 用法: ./stage0-simple.sh <project_dir> <output_file>

PROJECT_DIR="$1"
OUTPUT_FILE="$2"

if [ -z "$PROJECT_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <project_dir> <output_file>"
    exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_DIR")

echo "=== Stage 0: 确定性提取 $PROJECT_NAME ===" >&2

# 基本信息
echo "# repo_facts: $PROJECT_NAME" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 语言分布
echo "## 语言分布" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.java" -o -name "*.rs" \) \
    ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/venv/*" ! -path "*/__pycache__/*" \
    | sed 's/.*\.//' | sort | uniq -c | sort -rn >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 文件结构（顶层 + 二层）
echo "## 目录结构（前两层）" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -maxdepth 2 -type d ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/venv/*" | \
    sed "s|$PROJECT_DIR/||" | head -50 >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# README 内容（前100行）
echo "## README（前100行）" >> "$OUTPUT_FILE"
if [ -f "$PROJECT_DIR/README.md" ]; then
    head -100 "$PROJECT_DIR/README.md" >> "$OUTPUT_FILE"
elif [ -f "$PROJECT_DIR/README.rst" ]; then
    head -100 "$PROJECT_DIR/README.rst" >> "$OUTPUT_FILE"
else
    echo "(无 README)" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# 依赖文件
echo "## 依赖" >> "$OUTPUT_FILE"
for dep_file in requirements.txt setup.py setup.cfg pyproject.toml package.json Cargo.toml go.mod; do
    if [ -f "$PROJECT_DIR/$dep_file" ]; then
        echo "### $dep_file" >> "$OUTPUT_FILE"
        head -50 "$PROJECT_DIR/$dep_file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

# 配置文件
echo "## 配置文件" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -maxdepth 2 -type f \( -name "*.cfg" -o -name "*.ini" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
    ! -path "*/.git/*" ! -path "*/node_modules/*" ! -name "package-lock.json" ! -name "yarn.lock" \
    | sed "s|$PROJECT_DIR/||" | head -20 >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 核心 Python 文件（按大小排序，取前 10 个非 __init__.py）
echo "## 核心代码文件（按大小排序 Top 10）" >> "$OUTPUT_FILE"
find "$PROJECT_DIR" -type f -name "*.py" ! -name "__init__.py" ! -name "setup.py" \
    ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/venv/*" ! -path "*/migrations/*" \
    -exec wc -l {} \; 2>/dev/null | sort -rn | head -10 | \
    sed "s|$PROJECT_DIR/||" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 关键代码片段（最大的 3 个 py 文件的前 150 行）
echo "## 关键代码片段" >> "$OUTPUT_FILE"
TOP_FILES=$(find "$PROJECT_DIR" -type f -name "*.py" ! -name "__init__.py" ! -name "setup.py" \
    ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/venv/*" ! -path "*/migrations/*" \
    -exec wc -l {} \; 2>/dev/null | sort -rn | head -3 | awk '{print $2}')

for f in $TOP_FILES; do
    echo "### $(echo $f | sed "s|$PROJECT_DIR/||")" >> "$OUTPUT_FILE"
    echo '```python' >> "$OUTPUT_FILE"
    head -150 "$f" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done

# 入口文件
echo "## 入口文件" >> "$OUTPUT_FILE"
for entry in main.py app.py run.py manage.py __main__.py; do
    FOUND=$(find "$PROJECT_DIR" -maxdepth 2 -name "$entry" ! -path "*/.git/*" 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        echo "### $(echo $FOUND | sed "s|$PROJECT_DIR/||")" >> "$OUTPUT_FILE"
        echo '```python' >> "$OUTPUT_FILE"
        head -80 "$FOUND" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "=== Stage 0 完成: $OUTPUT_FILE ===" >&2
