#!/usr/bin/env python3
"""Generate Stage 4 expert narrative using Anthropic API."""
import json
import os
import sys
import urllib.request
import urllib.error

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
MODEL = os.environ.get("SOUL_MODEL", "claude-sonnet-4-6-20250514")

BASE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.join(BASE, "superpowers")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_all_cards(subdir):
    import glob
    cards_dir = os.path.join(SP, "soul", "cards", subdir)
    texts = []
    for f in sorted(glob.glob(os.path.join(cards_dir, "*.md"))):
        texts.append(f"### {os.path.basename(f)}\n{read_file(f)}")
    return "\n\n".join(texts)

# Read inputs
soul = read_file(os.path.join(SP, "soul", "00-project-essence.md"))
concepts = read_all_cards("concepts")
workflows = read_all_cards("workflows")
rules = read_all_cards("rules")
community = read_file(os.path.join(SP, "artifacts", "community_signals.md"))

system_prompt = """你是一个开源项目的顶级专家。你要把提取到的全部知识，合成为一次"专家对专家"的知识传递。
不是写文档。不是列规则。是像一个专家在对另一个专家说话。

约束：
- 设计哲学和心智模型从项目灵魂文件直接取，不要重写或稀释
- "为什么这样设计"必须有因果链，不是功能描述
- "踩坑故事"必须是叙事体（有人、有场景、有过程、有结果），不是规则条目
- 每个踩坑故事必须引用真实的 Issue 编号或 CHANGELOG 版本
- 整个文件控制在 1500 字以内
- 不要在叙事中重复规则卡的 DO/DON'T 列表——规则由组装脚本处理
- 叙事聚焦于"为什么"和"踩过什么坑"，不要写"怎么做"的指令
- 不要写速查规则表——速查由组装脚本自动从规则卡生成"""

user_prompt = f"""请基于以下知识，合成专家叙事文档。

## 项目灵魂
{soul}

## 概念卡
{concepts}

## 工作流卡
{workflows}

## 规则卡
{rules}

## 社区信号
{community[:3000]}

## 产出结构（必须严格遵循）

```markdown
# superpowers — AI 知识注入

## 设计哲学
[直接从项目灵魂的 Q6 取。像这个项目的创造者在对你说话。]

## 心智模型
[直接从项目灵魂的 Q7 取。一个类比或一句话。]

## 为什么这样设计
[从规则卡和概念卡中提炼 2-3 个核心设计决策。
 每个决策必须回答"为什么"而不是"是什么"。
 格式：因为相信 X → 所以设计了 Y → 这就是为什么规则 Z 存在。]

## 你一定会踩的坑
[从社区陷阱卡（DR-100~）和社区信号中提炼 3 个最重要的故事。
 每个故事必须是叙事体。附上 Issue 编号和 reactions 数。]
```

直接输出 markdown 内容，不要加任何前言或解释。"""

# Call API
body = json.dumps({
    "model": MODEL,
    "max_tokens": 4096,
    "temperature": 0.3,
    "system": system_prompt,
    "messages": [{"role": "user", "content": user_prompt}],
}).encode("utf-8")

req = urllib.request.Request(f"{BASE_URL}/v1/messages", data=body, headers={
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
})

print("Calling API...", file=sys.stderr)
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
    sys.exit(1)

result = "".join(b["text"] for b in data["content"] if b["type"] == "text")

# Write output
output_path = os.path.join(SP, "soul", "expert_narrative.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"Written to {output_path}", file=sys.stderr)
print(f"Length: {len(result)} chars", file=sys.stderr)
