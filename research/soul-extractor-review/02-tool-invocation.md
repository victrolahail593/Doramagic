# 工具调用评审报告

研究日期: 2026-03-10 | 模型: bailian/glm-5

## 现状分析

Soul Extractor v0.8 包含 5 个核心脚本，构成一个完整的知识提取流水线：

### 脚本概览

| 脚本 | 用途 | 语言 | 行数 |
|------|------|------|------|
| `prepare-repo.sh` | 仓库克隆 + Repomix 打包 | Bash | ~60 |
| `extract.py` | 核心提取逻辑（4阶段） | Python | ~280 |
| `collect-community-signals.py` | 社区信号收集 | Python | ~400 |
| `validate_extraction.py` | 硬验证与质量门控 | Python | ~380 |
| `assemble-output.sh` | 最终产出组装 | Bash | ~80 |

### 架构特点

```
prepare-repo.sh → [artifacts/]
       ↓
extract.py (Phase 0-4)
       ↓
collect-community-signals.py → [community_signals.md]
       ↓
validate_extraction.py → [validation_report.json]
       ↓
assemble-output.sh → [inject/]
```

---

## 问题发现

### 1. prepare-repo.sh

#### P0 - 阻塞性问题

| 问题 | 描述 | 影响 |
|------|------|------|
| **缺少依赖预检** | 未检查 `git`、`node`、`npx` 是否安装 | 用户看到 cryptic 错误 |
| **无仓库大小限制** | 大仓库（>500MB）可能导致磁盘耗尽或 repomix 超时 | 流程卡死 |
| **无网络超时控制** | `git clone` 和 GitHub API 无超时设置 | 中国网络环境易卡死 |

#### P1 - 重要问题

| 问题 | 描述 |
|------|------|
| **镜像重试无间隔** | 连续失败时没有退避策略，可能触发 GitHub rate limit |
| **错误信息不友好** | `exit 1` 无具体原因，用户难以排查 |
| **路径空格未处理** | `$REPO_INPUT` 和 `$OUTPUT_DIR` 未做引号保护 |

#### P2 - 改进建议

```bash
# 建议添加的预检逻辑
check_dependencies() {
    local missing=()
    command -v git >/dev/null || missing+=("git")
    command -v node >/dev/null || missing+=("node")
    command -v npx >/dev/null || missing+=("npx (npm)")
    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: Missing dependencies: ${missing[*]}"
        echo "Install: brew install ${missing[*]}"
        exit 1
    fi
}

# 建议添加的仓库大小检查
check_repo_size() {
    local max_mb=500
    local size=$(du -sm "$CLONE_DIR" 2>/dev/null | cut -f1)
    if [ "$size" -gt "$max_mb" ]; then
        echo "WARN: Repository is ${size}MB, extraction may be slow"
    fi
}
```

---

### 2. validate_extraction.py

#### P0 - 阻塞性问题

| 问题 | 描述 | 影响 |
|------|------|------|
| **YAML 解析器不完整** | 多行块标量（`|`）解析有边界情况 | 误判 card 无效 |
| **缺少 Mermaid 验证** | workflow card 要求 Mermaid 图，但无语法检查 | 漏报无效卡片 |
| **正则匹配脆弱** | `file:line` 模式 `^[^:]+\.\w+` 可能误匹配 URL | 假阳性/假阴性 |

#### P1 - 重要问题

| 问题 | 描述 |
|------|------|
| **无 schema 版本** | 格式变更时无法向后兼容 |
| **社区信号检查浅层** | 仅检查 `#123` 字符串存在，不验证实际内容关联 |
| **confidence 验证过松** | 非数值直接通过，而非报错 |

#### 潜在误报/漏报分析

```python
# 误报案例 1: 多行字符串解析
# 输入:
rule: |
  IF condition THEN
    behavior
# 当前解析器可能丢失换行

# 误报案例 2: 文件引用
sources:
  - "https://github.com/user/repo/blob/main/file.py#L42"
# 正则匹配会提取 "file.py" 但实际是 URL

# 漏报案例: 无效 Mermaid
# workflow card 包含 ```mermaid graph TD; ``` (空图)
# 当前验证通过，但实际无效
```

#### P2 - 改进建议

```python
# 建议: 添加 Mermaid 基础验证
def check_mermaid_syntax(body: str) -> List[str]:
    """Basic Mermaid syntax validation."""
    errors = []
    mermaid_match = re.search(r'```mermaid\s+(.+?)\s*```', body, re.DOTALL)
    if mermaid_match:
        code = mermaid_match.group(1).strip()
        if not code:
            errors.append("Empty Mermaid diagram")
        elif not any(kw in code for kw in ['-->', '---', '->', '->>', '=>']):
            errors.append("Mermaid diagram has no connections")
    return errors

# 建议: schema 版本控制
SCHEMA_VERSION = "0.8.0"
REQUIRED_DR_FIELDS_V0_8 = [...]
REQUIRED_DR_FIELDS_V0_9 = [...]  # 未来版本
```

---

### 3. assemble-output.sh

#### P1 - 重要问题

| 问题 | 描述 | 影响 |
|------|------|------|
| **验证失败仅警告** | `overall_pass=false` 时继续组装 | 质量无保障 |
| **glob 模式脆弱** | `CC-*.md` 匹配失败时静默跳过 | 输出不完整 |
| **依赖顺序未强制** | 未检查 Stage 0-4 是否已完成 | 运行时错误 |

#### P2 - 改进建议

```bash
# 建议: 强制验证门控
if [ -f "$VALIDATION_REPORT" ]; then
    if ! python3 -c "import json; r=json.load(open('$VALIDATION_REPORT')); exit(0 if r['summary']['overall_pass'] else 1)" 2>/dev/null; then
        echo "ERROR: Validation failed. Fix errors before assembly."
        echo "Run: python3 scripts/validate_extraction.py --output-dir '$OUTPUT_DIR'"
        exit 1  # 改为阻塞
    fi
fi

# 建议: 检查前置阶段
check_prerequisites() {
    local required=(
        "$SOUL_DIR/expert_narrative.md"
        "$OUTPUT_DIR/artifacts/packed_compressed.xml"
    )
    for f in "${required[@]}"; do
        [ -f "$f" ] || { echo "ERROR: Missing $f - run earlier stages first"; exit 1; }
    done
}
```

---

### 4. 跨平台兼容性

| 平台 | 问题 | 严重性 |
|------|------|--------|
| **Windows** | Bash 脚本需要 Git Bash/WSL；路径分隔符 `\` 未处理 | P0 |
| **Windows** | `npx` 路径 `~/` 不可用 | P1 |
| **macOS** | `wc -c` 输出格式不同（含空格） | P2 |
| **Linux** | 基本兼容 | - |

#### 解决方案建议

```bash
# 路径标准化
normalize_path() {
    echo "$1" | sed 's|\\|/|g'
}

# 跨平台 wc 输出
BYTES=$(wc -c < "$FILE" | tr -d '[:space:]')

# Windows 检测
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Windows detected - using Git Bash"
fi
```

---

### 5. 依赖管理

#### 当前依赖

| 依赖 | 版本要求 | 检查机制 |
|------|----------|----------|
| `git` | 任意 | 无 |
| `node` | 任意 | 无 |
| `npx` | npm 5.2+ | 无 |
| `repomix` | 最新 | 隐式安装 |
| `python3` | 3.8+ | 无 |
| `urllib` | stdlib | ✅ |
| `anthropic API key` | 必需 | ✅ 有检查 |
| `GITHUB_TOKEN` | 可选 | 无说明 |

#### 问题

1. **无版本锁定**: `npx repomix` 总是获取最新版，可能有 breaking change
2. **无依赖文档**: 用户不知道需要安装什么
3. **API key 环境变量名不一致**: `ANTHROPIC_API_KEY` vs `GITHUB_TOKEN`

#### 建议改进

```bash
# scripts/check-deps.sh
#!/bin/bash
# Soul Extractor dependency checker

check_version() {
    local cmd="$1" min="$2"
    local ver=$($cmd --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    if [ -z "$ver" ]; then
        echo "ERROR: $cmd not found"
        return 1
    fi
    # Version comparison...
}

# 锁定 repomix 版本
npx repomix@1.4.0 --compress --style xml

# 文档中明确依赖
# Requirements:
# - git >= 2.0
# - node >= 16.0
# - python >= 3.8
# - ANTHROPIC_API_KEY environment variable
# - GITHUB_TOKEN (optional, for higher rate limits)
```

---

## 改进建议

### 短期（P0 - 阻塞性）

1. **添加依赖检查脚本** `scripts/check-deps.sh`
   - 检查 git/node/python 版本
   - 验证 API key 已设置
   - 提供 installation guide 链接

2. **prepare-repo.sh 添加超时和大小限制**
   ```bash
   git clone --depth 1 --timeout 60 "$URL" "$DIR"
   du -sm "$DIR" | awk '{if ($1 > 500) exit 1}'
   ```

3. **Windows 兼容性文档**
   - 在 SKILL.md 中明确标注: "Requires Git Bash on Windows"
   - 或提供 PowerShell 替代脚本

### 中期（P1 - 重要）

4. **validate_extraction.py 增强**
   - 添加 Mermaid 语法基础验证
   - 改进多行 YAML 解析
   - 添加 schema 版本字段

5. **assemble-output.sh 硬化**
   - 验证失败时阻塞（可配置）
   - 检查前置阶段完成
   - 改进 glob 错误处理

6. **错误信息标准化**
   - 所有脚本统一错误格式
   - 提供错误码便于自动化处理

### 长期（P2 - 增强）

7. **版本锁定**
   - 创建 `requirements.txt` 和 `package.json`
   - 锁定 repomix 版本

8. **日志和可观测性**
   - 添加 `--verbose` 和 `--quiet` 模式
   - 输出结构化日志（JSON）供调试

9. **测试覆盖**
   - 添加示例仓库和预期输出
   - CI/CD 中运行验证测试

---

## 优先级排序

### P0 - 必须立即修复（阻塞使用）

| 序号 | 问题 | 影响 | 工作量 |
|------|------|------|--------|
| 1 | 缺少依赖预检 | 用户无法启动 | 2h |
| 2 | 无仓库大小/网络超时限制 | 流程卡死 | 1h |
| 3 | Windows 不兼容 | 50% 用户无法使用 | 4h |

### P1 - 本周修复（影响质量）

| 序号 | 问题 | 影响 | 工作量 |
|------|------|------|--------|
| 4 | YAML 解析边界情况 | 误报 | 3h |
| 5 | 验证失败仅警告 | 质量无保障 | 1h |
| 6 | 无 Mermaid 验证 | 漏报 | 2h |

### P2 - 下个版本（增强体验）

| 序号 | 问题 | 影响 | 工作量 |
|------|------|------|--------|
| 7 | 版本锁定 | 兼容性风险 | 2h |
| 8 | 错误信息标准化 | 用户体验 | 3h |
| 9 | 测试覆盖 | 维护成本 | 8h |

---

## 附录: 代码质量评分

| 脚本 | 可读性 | 健壮性 | 可维护性 | 总评 |
|------|--------|--------|----------|------|
| prepare-repo.sh | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | B |
| extract.py | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | B+ |
| collect-community-signals.py | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | A- |
| validate_extraction.py | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | B+ |
| assemble-output.sh | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | B |

**整体评价**: 架构清晰，核心逻辑完善，但边缘情况处理和跨平台兼容性需加强。建议优先解决 P0 问题后发布 v0.9。
