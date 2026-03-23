# 鲁棒性评审报告

研究日期: 2026-03-10 | 模型: glm-5

## 现状分析

### 整体架构
Soul Extractor v0.8 采用 6 阶段流水线设计：
- Stage 0: 准备（下载代码、打包、收集社区信号）
- Stage 1: 灵魂发现（设计哲学 + 心智模型）
- Stage 2: 概念卡 + 工作流卡提取
- Stage 3: 规则卡提取（代码规则 + 社区陷阱）
- Stage 3.5: 验证与审查
- Stage 4: 专家叙事合成
- Stage 5: 组装产出

### 鲁棒性设计亮点
1. **网络容错**：`prepare-repo.sh` 实现了 GitHub 镜像列表重试机制
2. **社区信号降级**：`collect-community-signals.py` 支持 local-only 模式，网络失败时继续处理
3. **硬验证门控**：`validate_extraction.py` 提供格式合规性检查，防止低质量产出
4. **YAML frontmatter 解析**：无依赖的轻量解析器，避免外部库故障

---

## 问题发现

### P0 级（阻塞性问题）

#### 1. 大仓库截断导致上下文丢失
**位置**: `extract.py:94-98`
```python
if len(compressed) > 150000:
    compressed = compressed[:150000] + "\n<!-- TRUNCATED -->"
```
**问题**: 
- 150KB 截断阈值对于大型项目（如 kubernetes, react）过于激进
- 截断发生在字符级别，可能在关键代码块中间切断
- 没有记录哪些文件/模块被截断，用户无法判断缺失范围
- STAGE-1-essence.md 要求基于"代码内容回答，不要编造"，但截断后 LLM 可能在缺失上下文的情况下编造

**影响**: 提取质量不可预测，可能产生错误的设计哲学和规则

#### 2. 验证失败的恢复路径不完整
**位置**: `STAGE-3.5-review.md` + `validate_extraction.py`

**问题**:
- 验证失败要求"修复所有 Errors"，但没有自动化修复建议
- `MIN_COMMUNITY_RULES = 3` 的硬性要求在小项目/新项目上无法满足
- 没有 `--skip-validation` 或 `--relax-requirements` 选项
- 用户可能陷入"无法通过验证 → 不知道怎么修 → 放弃使用"的死循环

**代码证据** (`validate_extraction.py:200-204`):
```python
if community_rule_count < MIN_COMMUNITY_RULES:
    quantity_errors.append(f"Only {community_rule_count} community rules (DR-10x), minimum {MIN_COMMUNITY_RULES}")
# ... 后续导致 overall_pass = False
```

#### 3. 无社区信号时的死循环
**场景**: 新项目、私有项目、非 GitHub 项目

**问题链**:
1. `collect-community-signals.py` 返回空的 community_signals.md
2. STAGE-3 规则卡要求 "社区陷阱至少 3 张"
3. LLM 无法从空数据中提取社区陷阱
4. 验证失败：`Only 0 community rules (DR-10x), minimum 3`
5. 无法修复 → 流程卡死

---

### P1 级（严重问题）

#### 4. 重复提取没有清理机制
**位置**: `prepare-repo.sh:22-39`

**问题**:
```bash
if [ ! -d "$CLONE_DIR" ]; then
    # 只有目录不存在才克隆
```
- 如果上次提取中途失败，残留数据会导致跳过克隆
- `packed_compressed.xml` 和 `packed_full.xml` 也有相同问题
- 用户可能得到混合版本的代码包

**测试验证**:
```bash
# 第一次运行中断
git clone --depth 1 ... && kill -9 $$

# 第二次运行
# 会跳过克隆，使用残留的不完整仓库
```

#### 5. 磁盘空间无检测
**问题**:
- 大型仓库 clone 可能需要数 GB 空间
- repomix 打包会生成 2 倍大小的输出文件
- 没有 `df` 检测或 `ENOSPC` 处理
- 磁盘满可能导致部分写入的损坏文件

**风险**: 用户在有限空间（如 Docker 容器）运行时，会产生难以诊断的损坏

#### 6. 非英文项目的 section 检查硬编码
**位置**: `validate_extraction.py:124-135`

```python
if "## 真实场景" not in body and "## Real" not in body:
    warnings.append("Missing '## 真实场景' section")
```

**问题**:
- 只支持中英文 section 名称
- 日文、韩文、德文项目会被误报 warning
- `STAGE-4-synthesis.md` 的示例是英文，但 section 检查优先中文

---

### P2 级（改进建议）

#### 7. 网络超时配置分散
**位置**: 
- `collect-community-signals.py:25-26` 定义了 `CONNECT_TIMEOUT = 10`, `REQUEST_TIMEOUT = 15`
- `extract.py` 的 API 调用硬编码 `timeout=300`
- `prepare-repo.sh` 的 git clone 没有超时控制

**建议**: 统一通过环境变量或配置文件管理

#### 8. LLM API 失败无重试
**位置**: `extract.py:41-49`

```python
except urllib.error.HTTPError as e:
    print(f"API error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)  # 直接退出，不重试
```

**问题**: 
- Anthropic API 偶发 529/503 错误
- 长时间运行的 LLM 调用（Phase 1-4）可能因临时故障全部丢失

#### 9. 卡片 ID 冲突检测不全面
**位置**: `validate_extraction.py:141-143`

```python
if card_id in seen_ids:
    errors.append(f"Duplicate card_id: {card_id}")
```

**问题**: 
- 只检测同一运行内的冲突
- 如果用户手动添加卡片并重新运行验证，可能产生跨运行冲突
- 没有 `--rename-duplicates` 自动修复

#### 10. repomix 缺失时的错误提示不清
**位置**: `prepare-repo.sh:47`

```bash
npx repomix --compress --style xml -o "$COMP" 2>&1
```

**问题**: 
- 如果 npx/node 不可用，错误信息会被 `2>&1` 吞没
- 用户看到的只是 "scripts/prepare-repo.sh: line 47: npx: command not found"
- 没有前置检查和友好提示

---

## 改进建议

### P0 修复（阻塞性）

#### 建议 1: 智能截断策略
```python
# 替换字符级截断为模块级截断
def smart_truncate(xml_content, max_chars=150000):
    # 1. 解析 XML 结构
    # 2. 按模块优先级排序（入口文件 > 核心模块 > 边缘模块）
    # 3. 保留完整模块，丢弃低优先级模块
    # 4. 记录被丢弃的模块列表
    pass
```

#### 建议 2: 社区信号降级策略
```python
# validate_extraction.py 增加降级逻辑
if community_rule_count < MIN_COMMUNITY_RULES:
    if community_signals_empty:
        # 社区信号为空是合理情况，跳过此项检查
        logger.info("No community signals found, relaxing requirement")
    else:
        quantity_errors.append(...)
```

#### 建议 3: 增加恢复命令
```bash
# prepare-repo.sh 增加 --clean 和 --resume 选项
--clean)   # 完全清理后重新开始
--resume)  # 检测并恢复中断的操作
```

### P1 修复（严重）

#### 建议 4: 磁盘空间预检
```bash
# prepare-repo.sh 开头增加
check_disk_space() {
    local required_mb=1024  # 默认 1GB
    local available=$(df -m "$OUTPUT_DIR" | awk 'NR==2 {print $4}')
    if [ "$available" -lt "$required_mb" ]; then
        echo "ERROR: Insufficient disk space. Required: ${required_mb}MB, Available: ${available}MB"
        exit 1
    fi
}
```

#### 建议 5: 多语言 section 检查
```python
# validate_extraction.py 使用正则匹配
SECTION_PATTERNS = {
    'real_scenario': r'## (真实场景|Real|Scénario réel|実シナリオ)',
    'impact': r'## (影响范围|Impact|Auswirkungen|影響範囲)',
}
```

#### 建议 6: LLM API 重试
```python
# extract.py 增加重试装饰器
@retry(max_attempts=3, backoff=exponential, retry_on=(HTTPError, TimeoutError))
def call_llm(system_prompt, user_prompt, temperature=0.3):
    ...
```

### P2 修复（改进）

#### 建议 7: 统一超时配置
```yaml
# 建议增加 soul-extractor.yaml
timeouts:
  connect: 10
  request: 15
  api: 300
  clone: 600
```

#### 建议 8: 前置依赖检查
```bash
# prepare-repo.sh 开头
check_dependencies() {
    local missing=()
    command -v node >/dev/null || missing+=("node")
    command -v npx >/dev/null || missing+=("npx")
    command -v git >/dev/null || missing+=("git")
    command -v python3 >/dev/null || missing+=("python3")
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: Missing required tools: ${missing[*]}"
        echo "Install with: brew install ${missing[*]}"
        exit 1
    fi
}
```

---

## 优先级排序

| 优先级 | 问题 | 影响范围 | 修复成本 |
|--------|------|----------|----------|
| P0-1 | 大仓库截断丢失上下文 | 大型项目无法使用 | 高 |
| P0-2 | 验证失败无恢复路径 | 小项目/新项目卡死 | 中 |
| P0-3 | 无社区信号时死循环 | 非GitHub/私有项目 | 低 |
| P1-4 | 重复提取数据污染 | 结果不可预测 | 中 |
| P1-5 | 磁盘空间无检测 | Docker/容器环境 | 低 |
| P1-6 | 非英文项目误报 | 国际化项目 | 低 |
| P2-7 | 超时配置分散 | 运维调优困难 | 低 |
| P2-8 | LLM API 无重试 | 临时故障全丢 | 低 |
| P2-9 | 卡片ID跨运行冲突 | 手动编辑场景 | 低 |
| P2-10 | 依赖缺失提示不清 | 新用户体验 | 低 |

---

## 测试边界情况建议

建议增加以下自动化测试用例：

1. **大仓库测试**: kubernetes/kubernetes (1GB+ 代码)
2. **空社区测试**: 新创建的 GitHub 仓库
3. **非 GitHub 测试**: GitLab/Gitee 仓库
4. **非英文测试**: 包含日文/中文注释的项目
5. **中断恢复测试**: 模拟 Ctrl+C 后重新运行
6. **磁盘满测试**: 在有限空间容器中运行
7. **网络断开测试**: 在 API 调用期间切断网络

---

## 结论

Soul Extractor 的核心流程设计合理，但在边界情况处理上存在明显的鲁棒性缺口。最严重的问题是：

1. **大型项目支持不完整**：150KB 截断可能导致关键代码丢失
2. **零社区信号场景未处理**：新项目/私有项目无法完成流程
3. **错误恢复依赖人工**：验证失败后没有自动化修复建议

建议优先修复 P0 级问题，使工具能够适用于更广泛的项目类型。
