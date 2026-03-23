# Doramagic 知识卡片格式设计文档

**研究主题**：Doramagic 知识卡片存储格式设计  
**研究日期**：2026年3月11日  
**研究目的**：定义灵魂提取结果的统一存储格式，支持高效检索和系统集成

---

## 执行摘要

本设计文档为 Doramagic 的灵魂提取结果定义统一的存储格式。基于对现有系统的调研（MEMORY.md、SKILL 结构、soul-extractor），我们推荐采用 **YAML Frontmatter + Markdown** 的混合格式，兼顾可读性和机器可解析性。存储位置建议为 `~/Documents/openclaw/Doramagic/knowledge/` 目录，采用项目分组的层级结构。

---

## 1. 知识卡片内容设计

### 1.1 核心字段定义

每张知识卡片包含以下核心字段：

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `id` | ✅ | string | 全局唯一标识，格式：`KC-{project}-{type}-{number}` |
| `type` | ✅ | enum | 卡片类型：concept/workflow/decision/pitfall/resource |
| `title` | ✅ | string | 卡片标题 |
| `project` | ✅ | string | 来源项目名 |
| `project_url` | - | string | 项目仓库 URL |
| `version` | - | string | 项目版本/标签 |
| `evidence_level` | ✅ | enum | 证据等级：E1/E2/E3/E4 |
| `created_at` | ✅ | ISO8601 | 创建时间 |
| `updated_at` | - | ISO8601 | 更新时间 |
| `tags` | - | array[string] | 标签列表 |
| `language` | - | string | 主要语言/框架 |
| `author` | - | string | 提取作者 |

### 1.2 卡片类型详解

#### 1.2.1 概念卡片 (concept_card)

用于存储核心概念、定义和原理。

```yaml
---
id: KC-react-hooks-concept-001
type: concept_card
title: React Hooks 的闭包陷阱
project: react
project_url: https://github.com/facebook/react
evidence_level: E1
created_at: 2026-03-11T10:00:00Z
tags: [react, hooks, closure, pitfall]
language: TypeScript
author: doramagic
---

# React Hooks 的闭包陷阱

## 定义
在 React Hooks 中，由于闭包作用域，事件处理器捕获的是创建时的状态快照，而非最新值。

## 为什么重要
导致常见的 "stale closure" bug，状态更新不生效。

## 边界
- 这是 JS 闭包特性，不是 React bug
- 类组件同样存在此问题（但表现不同）

## 通俗解释
> 想象你在餐厅排队，前面的人点完餐后把点餐单保存在手里——即使餐厅菜单变了，他手里的单子还是旧的。

## 示例代码

```jsx
// ❌ 错误：count 始终是 0
useEffect(() => {
  const timer = setInterval(() => {
    console.log(count) // 始终打印 0
  }, 1000)
  return () => clearInterval(timer)
}, []) // 空依赖数组！

// ✅ 正确：使用函数式更新
useEffect(() => {
  const timer = setInterval(() => {
    setCount(c => c + 1) // 使用最新值
  }, 1000)
  return () => clearInterval(timer)
}, [])
```

## 相关卡片
- [KC-react-hooks-concept-002](./KC-react-hooks-concept-002.md) - useEffect 依赖数组
- [KC-react-workflow-001](./KC-react-workflow-001.md) - 自定义 Hook 开发流程
```

#### 1.2.2 工作流卡片 (workflow_card)

用于存储操作流程、最佳实践步骤。

```yaml
---
id: KC-nextjs-workflow-001
type: workflow_card
title: Next.js App Router 项目初始化
project: next.js
project_url: https://github.com/vercel/next.js
evidence_level: E1
created_at: 2026-03-11T10:30:00Z
tags: [nextjs, setup, app-router]
language: TypeScript
author: doramagic
---

# Next.js App Router 项目初始化

## 目的
从零开始创建一个生产级的 Next.js App Router 项目。

## 前置条件
- Node.js 18+
- npm/yarn/pnpm

## 步骤

### Step 1: 创建项目
```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint
```

### Step 2: 配置路径别名
默认已配置 `@/*` 指向 `./src/*`

### Step 3: 创建页面
在 `app/` 目录下创建 `page.tsx`

### Step 4: 启动开发服务器
```bash
npm run dev
```

## 结果
- 可访问的本地服务器：http://localhost:3000
- TypeScript + ESLint + Tailwind CSS 配置完成

## 常见问题
- **端口被占用**：使用 `npm run dev -- -p 3001` 指定端口
- **缓存问题**：运行 `rm -rf .next` 清理缓存
```

#### 1.2.3 决策规则卡片 (decision_rule_card)

用于存储设计决策、选型建议、规则约束。

```yaml
---
id: KC-nextjs-decision-001
type: decision_rule_card
title: Server Components vs Client Components 选择
project: next.js
project_url: https://github.com/vercel/next.js
evidence_level: E2
created_at: 2026-03-11T11:00:00Z
tags: [nextjs, server-components, client-components]
language: TypeScript
author: doramagic
---

# Server Components vs Client Components 选择

## 触发条件
在 Next.js App Router 中创建新组件时

## 决策规则

### 默认选择 Server Component
- 只需要渲染 UI
- 不需要交互（onClick, onChange 等）
- 不需要浏览器 API（window, document）
- 需要获取数据

### 选择 Client Component
- 需要使用 React Hooks（useState, useEffect, useRef）
- 需要事件处理器（onClick, onChange）
- 需要浏览器 API
- 需要第三方库（且这些库依赖客户端 API）

## 决策原因
1. **性能**：Server Components 减少客户端 JavaScript 体积
2. **数据获取**：Server Component 直接访问数据库/后端服务
3. **安全**：敏感逻辑（API keys）在服务端

## 边界/例外
- 可以在 Server Component 中使用 `<ClientComponent />`
- 下一代 React Compiler 会自动优化
- 某些库暂不支持 Server Component

## 通俗解释
> 想象餐厅服务员（Server）：负责点单、传菜、结账；顾客自己（Client）：吃饭、拍照、聊天
```

#### 1.2.4 踩坑卡片 (pitfall_card)

用于存储社区经验、常见错误、workaround 方案。

```yaml
---
id: KC-nextjs-pitfall-001
type: pitfall_card
title: Next.js 静态资源在 public 目录但 404
project: next.js
project_url: https://github.com/vercel/next.js
evidence_level: E3
created_at: 2026-03-11T11:30:00Z
tags: [nextjs, static-assets, pitfall]
language: TypeScript
author: doramagic
---

# Next.js 静态资源在 public 目录但 404

## 问题描述
把图片放入 `public/images/logo.png`，但在组件中引用 `src="/images/logo.png"` 时 404。

## 触发条件
- 首次部署到 Vercel
- 使用某些部署平台

## 根本原因
Vercel 部署时路径处理差异，静态资源路径需要相对路径或使用 `import` 导入。

## 解决方案

### 方案 1：使用 import（推荐）
```tsx
import logo from '../public/images/logo.png'

export default function Page() {
  return <img src={logo.src} alt="Logo" />
}
```

### 方案 2：使用相对路径
```tsx
// 在生产环境自动解析为正确路径
<img src="./images/logo.png" alt="Logo" />
```

### 方案 3：配置 next.config.js
```js
module.exports = {
  images: {
    unoptimized: true
  }
}
```

## 验证方法
```bash
curl -I https://your-domain.com/images/logo.png
```

## 相关问题
- Next.js Image 组件的默认行为
- Vercel 边缘函数的静态文件处理
```

#### 1.2.5 资源卡片 (resource_card)

用于存储推荐资源、学习链接、工具推荐。

```yaml
---
id: KC-react-resource-001
type: resource_card
title: React 官方学习资源汇总
project: react
project_url: https://github.com/facebook/react
evidence_level: E1
created_at: 2026-03-11T12:00:00Z
tags: [react, learning, resources]
author: doramagic
---

# React 官方学习资源汇总

## 官方文档
- **React 官方文档**: https://react.dev
- **React Hooks 专题**: https://react.dev/reference/react
- **Next.js 文档**: https://nextjs.org/docs

## 视频教程
- **React 官方教程**: https://react.dev/learn
- **Josh Comeau**: https://courses.joshwcomeau.com/

## 社区资源
- **Reactiflux Discord**: https://discord.gg/reactiflux
- **React Subreddit**: https://reddit.com/r/reactjs

## 工具推荐
- **React DevTools**: 浏览器插件
- **React Query DevTools**: 状态管理调试

## 免费课程
- **Scrimba**: https://scrimba.com/learn/learnreact
- **Frontend Mentor**: https://www.frontendmentor.io/
```

### 1.3 证据等级体系

沿用 soul-extractor 的证据等级体系：

| 等级 | 来源 | 可信度 | 适用场景 |
|------|------|--------|----------|
| E1 | 源码、测试、官方文档 | ⭐⭐⭐⭐⭐ | 核心概念、API 用法 |
| E2 | Maintainer issue/PR/release note | ⭐⭐⭐⭐ | 设计决策、版本特性 |
| E3 | 高质量社区共识、多次复现 | ⭐⭐⭐ | 踩坑经验、workaround |
| E4 | 弱传闻证据 | ⭐⭐ | 边缘情况、性能调优 |

---

## 2. 文件格式设计

### 2.1 格式选择：YAML Frontmatter + Markdown

**推荐格式**：采用 YAML Frontmatter（元数据头）+ Markdown（内容体）的混合格式。

**理由**：
1. **可读性**：纯文本，人类可直接阅读和编辑
2. **可解析**：前端可轻松解析 YAML 提取元数据
3. **生态支持**：VS Code、Obsidian 等工具原生支持
4. **版本控制**：diff 友好，适合 Git 管理

### 2.2 文件命名规范

```
KC-{project}-{type}-{number}.md
```

示例：
- `KC-react-hooks-concept-001.md`
- `KC-nextjs-workflow-001.md`
- `KC-python-pitfall-023.md`

### 2.3 快速检索设计

#### 2.3.1 索引文件

每个项目目录下维护 `INDEX.md` 索引文件：

```yaml
---
type: knowledge_index
project: react
total_cards: 15
last_updated: 2026-03-11T12:00:00Z
---

# React 知识卡片索引

## 概念卡 (3)
- [KC-react-hooks-concept-001](./KC-react-hooks-concept-001.md) - React Hooks 的闭包陷阱
- [KC-react-hooks-concept-002](./KC-react-hooks-concept-002.md) - useEffect 依赖数组
- ...

## 工作流卡 (5)
- [KC-react-workflow-001](./KC-react-workflow-001.md) - 自定义 Hook 开发流程
- ...

## 决策卡 (4)
- ...

## 踩坑卡 (2)
- ...

## 资源卡 (1)
- ...
```

#### 2.3.2 全局索引

维护顶层 `knowledge_index.json` 供程序化检索：

```json
{
  "version": "1.0",
  "last_updated": "2026-03-11T12:00:00Z",
  "projects": [
    {
      "name": "react",
      "path": "./react",
      "card_count": 15,
      "tags": ["react", "hooks", "state", "performance"]
    },
    {
      "name": "next.js",
      "path": "./nextjs",
      "card_count": 23,
      "tags": ["nextjs", "app-router", "ssr", "server-components"]
    }
  ],
  "global_tags": [
    {"name": "react", "count": 15},
    {"name": "hooks", "count": 8},
    {"name": "pitfall", "count": 12}
  ]
}
```

---

## 3. 存储位置设计

### 3.1 目录结构

```
~/Documents/openclaw/Doramagic/
├── knowledge/                    # 知识卡片根目录
│   ├── _index.json              # 全局索引
│   ├── _index.md                # 全局索引（人类可读）
│   ├── react/                   # 按项目分组
│   │   ├── INDEX.md
│   │   ├── _metadata.yaml
│   │   ├── concept/
│   │   │   └── KC-react-*.md
│   │   ├── workflow/
│   │   │   └── KC-react-*.md
│   │   ├── decision/
│   │   ├── pitfall/
│   │   └── resource/
│   ├── nextjs/
│   │   └── ...
│   └── python/
│       └── ...
├── research/                    # 研究文档
├── skills/                      # 已安装的 Skill
└── scripts/                     # 工具脚本
```

### 3.2 存储路径选择

**推荐路径**：`~/Documents/openclaw/Doramagic/knowledge/`

**理由**：
1. 与 OpenClaw 主工作区分离，避免污染
2. 位于 `Documents` 目录，易于备份和同步
3. 符合 Doramagic 项目自身的目录结构
4. 避免与 `~/.agents/skills/` 冲突（那是系统 skill 位置）

### 3.3 文件命名规则

| 类型 | 前缀 | 示例 |
|------|------|------|
| 概念卡 | KC-{project}-concept- | KC-react-concept-001.md |
| 工作流卡 | KC-{project}-workflow- | KC-nextjs-workflow-001.md |
| 决策卡 | KC-{project}-decision- | KC-python-decision-001.md |
| 踩坑卡 | KC-{project}-pitfall- | KC-nextjs-pitfall-001.md |
| 资源卡 | KC-{project}-resource- | KC-react-resource-001.md |

---

## 4. 读写接口设计

### 4.1 读取接口

#### 4.1.1 CLI 命令设计

```bash
# 搜索知识卡片
doramagic search <keyword>
doramagic search --project react
doramagic search --tag hooks
doramagic search --type pitfall

# 列出项目知识
doramagic list
doramagic list --project react

# 查看卡片详情
doramagic show KC-react-concept-001

# 列出某类型的卡片
doramagic list --type pitfall
```

#### 4.1.2 API 设计

```typescript
interface KnowledgeCard {
  id: string;
  type: 'concept' | 'workflow' | 'decision' | 'pitfall' | 'resource';
  title: string;
  project: string;
  evidence_level: 'E1' | 'E2' | 'E3' | 'E4';
  tags: string[];
  content: string;
  created_at: string;
  updated_at?: string;
}

class KnowledgeStore {
  // 搜索
  search(query: string, options?: SearchOptions): Promise<KnowledgeCard[]>;
  
  // 按项目获取
  getByProject(project: string): Promise<KnowledgeCard[]>;
  
  // 按类型获取
  getByType(type: CardType): Promise<KnowledgeCard[]>;
  
  // 按标签获取
  getByTag(tag: string): Promise<KnowledgeCard[]>;
  
  // 获取单张卡片
  get(id: string): Promise<KnowledgeCard | null>;
  
  // 获取索引
  getIndex(): Promise<KnowledgeIndex>;
}
```

### 4.2 写入接口

#### 4.2.1 创建新卡片

```bash
# 交互式创建
doramagic create
doramagic create --project react --type concept

# 从模板创建
doramagic create --template pitfall
```

#### 4.2.2 批量导入

```bash
# 从 soul-extractor 导入
doramagic import --from soul-extractor ./output/cards/

# 从 Markdown 文件导入
doramagic import ./my-cards/
```

#### 4.2.3 更新卡片

```bash
# 编辑卡片
doramagic edit KC-react-concept-001

# 更新元数据
doramagic update KC-react-concept-001 --tag "new-tag"

# 标记过时
doramagic deprecate KC-react-concept-001 --reason "已被新版 API 替代"
```

### 4.3 写入 API

```typescript
class KnowledgeStore {
  // 创建卡片
  async create(card: CreateCardRequest): Promise<KnowledgeCard>;
  
  // 更新卡片
  async update(id: string, updates: Partial<KnowledgeCard>): Promise<KnowledgeCard>;
  
  // 删除卡片
  async delete(id: string): Promise<void>;
  
  // 批量导入
  async importFromDirectory(dirPath: string): Promise<ImportResult>;
  
  // 重建索引
  async rebuildIndex(): Promise<void>;
}
```

---

## 5. 与现有系统的兼容设计

### 5.1 与 MEMORY.md 的共存策略

**定位差异**：
| 系统 | 定位 | 内容类型 | 更新频率 |
|------|------|----------|----------|
| MEMORY.md | OpenClaw 主记忆 | 经验教训、待办、日志 | 每次会话 |
| Doramagic Knowledge | 项目知识库 | 概念、流程、决策、踩坑 | 提取时 |

**共存原则**：
1. **各司其职**：MEMORY.md 存会话级/个人级经验；Knowledge 存项目级/复用级知识
2. **交叉引用**：可在 MEMORY.md 中引用 Knowledge 卡片：`参见 KC-react-concept-001`
3. **不重复**：不在两处同时存储相同内容

### 5.2 不影响 OpenClaw 性能的策略

1. **延迟加载**：知识卡片按需加载，不在启动时全部读入
2. **索引缓存**：索引文件缓存于内存，磁盘 I/O 最小化
3. **增量更新**：只更新修改的卡片，不重写整个目录
4. **独立目录**：知识库独立于 OpenClaw 主目录，避免扫描开销

### 5.3 与 soul-extractor 的集成

soul-extractor 产出的中间素材可直接导入：

```
soul-extractor 输出
    ↓
{output}/soul/cards/
    ↓
doramagic import --from soul-extractor
    ↓
标准化后的 Knowledge 卡片
```

---

## 6. 实现优先级

### Phase 1: 核心功能（MVP）
- [ ] 目录结构创建
- [ ] 卡片模板定义
- [ ] 手动创建/编辑卡片
- [ ] 基本搜索功能

### Phase 2: 工具链
- [ ] CLI 工具开发
- [ ] 索引自动更新
- [ ] 与 soul-extractor 集成

### Phase 3: 高级功能
- [ ] 向量搜索支持
- [ ] 卡片版本管理
- [ ] 社区贡献流程

---

## 7. 附录

### 7.1 卡片 ID 生成规则

```
KC-{project}-{type}-{number}

其中：
- project: 项目名（小写，横线分隔）
- type: concept/workflow/decision/pitfall/resource
- number: 3 位序号，从 001 开始
```

### 7.2 标签规范

- 使用小写
- 使用横线分隔多词标签
- 推荐标签：`react`, `hooks`, `state-management`, `ssr`, `performance`, `pitfall`, `best-practice`

### 7.3 示例文件

完整示例见： `./examples/KC-react-concept-001.md`

---

*文档版本：1.0.0*  
*创建时间：2026年3月11日*
