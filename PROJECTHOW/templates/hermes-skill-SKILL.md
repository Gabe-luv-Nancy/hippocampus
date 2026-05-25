---
name: hippo-memory-injection
description: HIPPO记忆注入协议——让Agent定期将对话中的关键信息写入 ~/.hippo_memory/ 标准记忆目录，实现持久化知识管理
category: productivity
version: 1.0.0
author: HIPPO-PROJECTHOW
triggers:
  - important_decision
  - technical_discovery
  - user_correction
  - knowledge_consolidation
---

# 🦛 HIPPO 记忆注入协议

> **使命**：在对话过程中，自动将关键信息以结构化方式写入 `~/.hippo_memory/` 目录，确保知识在对话之间持久留存。

---

## 一、目录结构（HIPPO 标准记忆格式）

```
~/.hippo_memory/
├── identity.yaml              ← Agent 身份卡（首次运行时创建）
├── daily/                     ← 日记忆（每天一份）
│   └── {YYYY-MM-DD}.md
├── weekly/                    ← 周归档
│   └── {YYYY}-W{NN}.md
├── knowledge/                 ← 知识卡片
│   └── {topic-slug}.md
├── preferences/               ← 用户偏好
│   └── {category}.yaml
└── meta/
    └── injection.yaml         ← 注入元数据（统计、最近写入时间等）
```

---

## 二、触发条件

在以下场景中**自动触发**记忆写入，无需用户显式指令：

| 触发类型 | 判断标准 | 示例 |
|---------|---------|------|
| 📌 重要决策 | 确定了技术选型、架构方案、流程变更等不可逆选择 | "决定使用 SQLite 而非 JSON 存储状态" |
| 🔧 技术发现 | 发现了非显而易见的技术事实、踩坑经验、API 行为 | "发现 WSL 中符号链接跨盘不生效" |
| ⚠️ 用户纠正 | 用户明确纠正了 Agent 的理解或输出 | "不是 Python 3.9，是 3.11" |
| 🧠 知识沉淀 | 对话中产出了可复用的结构化知识 | 整理出了配置模板、命令速查表 |
| 📋 待跟进 | 明确标记的后续任务或待验证事项 | "明天需要确认 API 限流策略" |
| ❤️ 偏好记录 | 用户表达了稳定的工作偏好 | "用户习惯用中文交流" |

**不触发的场景**：
- ❌ 临时性闲聊（今天吃了什么、天气如何）
- ❌ 已过时的任务进度（"刚才第3步完成了"）
- ❌ 纯情绪表达、寒暄
- ❌ 纯中间过程信息（只有在最终确认后才写入）

---

## 三、日记忆写入规则

### 3.1 文件路径

```
~/.hippo_memory/daily/{YYYY-MM-DD}.md
```

日期取当前系统日期，格式 `YYYY-MM-DD`（如 `2025-05-22`）。

### 3.2 文件头（每日首次创建时写入）

```markdown
# 📅 {YYYY-MM-DD} 日记忆

> 自动生成于 {YYYY-MM-DD HH:mm} | HIPPO Memory Injection Protocol

---
```

**判断是否需要创建文件头**：先用 `read_file` 尝试读取当日文件。如果文件不存在（工具返回错误），则创建新文件并写入文件头。如果文件已存在，则直接在末尾**追加**内容。

### 3.3 追加格式

每次触发写入时，根据类型在对应章节下追加条目。完整章节结构如下：

```markdown
## 📌 今日关键决策

- **[{HH:mm}]** {决策描述} — 原因：{为什么这么决定}
  - 影响范围：{影响的模块/文件/流程}
  - 相关上下文：{简要背景}

## 🔧 技术发现

- **[{HH:mm}]** {发现描述}
  - 详情：{具体行为或配置}
  - 验证方式：{如何确认的}
  - 适用范围：{在什么条件下成立}

## ⚠️ 纠正与教训

- **[{HH:mm}]** {被纠正的内容} → {正确理解}
  - 教训：{记住什么}
  - 根因：{为什么会搞错}

## 📋 待跟进

- **[{HH:mm}]** {待办事项} — 截止：{时间/条件} | 优先级：{高/中/低}

## 🧠 知识沉淀

- **[{HH:mm}]** {知识标题}
  - 内容：{结构化知识}
  - 标签：`{tag1}` `{tag2}`
```

### 3.4 写入操作步骤

```
1. 计算当日文件路径: ~/.hippo_memory/daily/{YYYY-MM-DD}.md
2. 尝试 read_file 该路径
3. 如果文件不存在 → 用 write_file 创建，包含文件头 + 本次条目
4. 如果文件已存在 → 拼接现有内容 + 本次条目，用 write_file 覆写
5. 更新 meta/injection.yaml 中的 last_write 时间
```

### 3.5 文件大小控制

- 每份日记忆文件**不超过 5KB**（约 150-200 行 Markdown）
- 当文件接近上限时，优先保留：
  - 关键决策 > 技术发现 > 知识沉淀 > 待跟进 > 纠正与教训
- 如果当日文件已超限，考虑将早期条目压缩为摘要

---

## 四、周归档规则

### 4.1 触发时机

每个**周一**（或在周一的首次对话中），自动执行上周归档：

```
1. 收集 ~/.hippo_memory/daily/ 下上周一至周日的所有 .md 文件
2. 合并、去重、压缩为一份周摘要
3. 写入 ~/.hippo_memory/weekly/{YYYY}-W{NN}.md
```

### 4.2 周归档文件路径

```
~/.hippo_memory/weekly/{YYYY}-W{NN}.md
```

其中 `{NN}` 为 ISO 周号（如 `2025-W21`）。

### 4.3 周归档格式

```markdown
# 📊 {YYYY} 年第 {NN} 周归档

> 自动生成于 {YYYY-MM-DD HH:mm} | 覆盖范围：{起始日期} ~ {结束日期}

---

## 📌 本周关键决策汇总

1. {决策1} — {原因简述}
2. {决策2} — {原因简述}

## 🔧 重要技术发现

- {发现1}：{一句话概括}
- {发现2}：{一句话概括}

## ⚠️ 主要教训

- {教训1}
- {教训2}

## 📋 待办遗留（未完成的跟进项）

- [ ] {待办1}
- [ ] {待办2}

## 📈 本周统计

- 活跃天数：{N} 天
- 决策数量：{N} 条
- 技术发现：{N} 条
- 知识沉淀：{N} 条
```

---

## 五、identity.yaml 初始化

### 5.1 触发条件

首次执行记忆写入时，检查 `~/.hippo_memory/identity.yaml` 是否存在。如果不存在，自动创建。

### 5.2 identity.yaml 模板

```yaml
# HIPPO Agent 身份卡
# 自动生成，请勿手动修改（除非你知道自己在做什么）

agent:
  name: "Hermes Agent"
  protocol: "HIPPO Memory Injection v1.0"
  created_at: "{YYYY-MM-DD HH:mm}"
  last_active: "{YYYY-MM-DD HH:mm}"

memory_stats:
  total_daily_files: 0
  total_weekly_files: 0
  total_knowledge_cards: 0
  total_writes: 0

preferences:
  language: "zh-CN"
  timezone: "Asia/Shanghai"
  max_daily_file_size: "5KB"
```

### 5.3 后续更新

每次写入操作后，更新 `last_active` 字段和 `memory_stats` 中的计数器。

---

## 六、meta/injection.yaml 维护

### 6.1 文件路径

```
~/.hippo_memory/meta/injection.yaml
```

### 6.2 内容格式

```yaml
# HIPPO 注入元数据
# 记录记忆写入的统计信息

last_write:
  timestamp: "{YYYY-MM-DD HH:mm}"
  type: "{daily|weekly|knowledge|preference}"
  file: "{写入的文件路径}"

write_history:
  - date: "{YYYY-MM-DD}"
    types: ["daily", "knowledge"]
    entries: 3

stats:
  total_writes: 0
  daily_files_created: 0
  weekly_files_created: 0
  knowledge_cards_created: 0
```

---

## 七、知识卡片写入规则

### 7.1 触发条件

当对话中产出了**高度结构化、可独立复用**的知识时，写入知识卡片。

### 7.2 文件路径

```
~/.hippo_memory/knowledge/{topic-slug}.md
```

其中 `{topic-slug}` 为英文短横线连接的主题标识（如 `docker-wsl-setup`、`git-subtree-usage`）。

### 7.3 格式

```markdown
# {知识标题}

> 创建于 {YYYY-MM-DD} | 最后更新于 {YYYY-MM-DD}
> 来源：{对话/文档/实验} | 标签：`{tag1}` `{tag2}`

---

## 概述

{一句话概括这条知识}

## 详细内容

{结构化知识正文}

## 示例

\```
{代码示例或命令示例}
\```

## 注意事项

- {注意事项1}
- {注意事项2}

## 相关链接

- {参考链接1}
```

---

## 八、用户偏好记录规则

### 8.1 触发条件

用户明确表达了工作偏好、习惯、风格倾向，且该偏好具有**长期稳定性**。

### 8.2 文件路径

```
~/.hippo_memory/preferences/{category}.yaml
```

### 8.3 常见分类

| 文件名 | 记录内容 |
|-------|---------|
| `language.yaml` | 语言偏好、术语习惯 |
| `coding.yaml` | 代码风格、命名规范、框架偏好 |
| `workflow.yaml` | 工作流、工具链、自动化偏好 |
| `communication.yaml` | 沟通风格、回复详略度偏好 |

### 8.4 格式示例

```yaml
# 用户偏好 - 编码风格
# 最后更新：{YYYY-MM-DD}

preferences:
  language: "中文为主，技术术语用英文"
  indent: "2 spaces"
  framework_preference: "React over Vue"
  api_style: "RESTful"
```

---

## 九、常见陷阱（必读 ⛔）

> 以下是执行记忆写入时**必须避免**的错误：

### 9.1 不记录临时性信息

```
❌ 错误：记录"用户今天中午吃了面条"
✅ 正确：记录"用户对意大利面烹饪有专业级知识"
```

**原则**：每条记忆必须是一个 **durable fact**——在未来一个月内仍然有意义。

### 9.2 不记录已过时的任务进度

```
❌ 错误：记录"第3步已完成，正在进行第4步"
✅ 正确：记录"整个流程已确定7步方案，核心步骤是第3步的XXX"
```

**原则**：记录**方案和结论**，而非**进度状态**。进度是瞬时的，结论是持久的。

### 9.3 不重复记录

```
❌ 错误：同一条知识在3次对话中分别写入了3次
✅ 正确：第一次写入，后续只更新已有卡片
```

**原则**：写入前先检查是否已有相同主题的知识卡片或条目。

### 9.4 不写入空洞内容

```
❌ 错误："讨论了一些技术问题"
✅ 正确："确认了 SQLite WAL 模式在高并发读场景下的性能优势"
```

**原则**：每条记忆必须包含**具体、可操作的信息**。

### 9.5 文件大小控制

```
❌ 错误：日记忆文件膨胀到 50KB
✅ 正确：严格控制在 5KB 以内，及时压缩归档
```

**原则**：记忆的价值在于**精炼**，而非**完整**。

### 9.6 不泄露敏感信息

```
❌ 错误：记录完整的 API Key、密码、Token
✅ 正确：记录"已在 .env 中配置了 API Key，provider 是 OpenAI"
```

**原则**：记忆文件是**明文存储**，绝对不能包含任何凭证信息。

---

## 十、执行流程总结

```
对话进行中
    │
    ├── 检测到触发条件？
    │   ├── 否 → 继续正常对话
    │   └── 是 ↓
    │
    ├── 首次运行检查
    │   ├── identity.yaml 存在？ → 否 → 创建
    │   ├── meta/injection.yaml 存在？ → 否 → 创建
    │   └── ~/.hippo_memory/ 子目录存在？ → 否 → 创建
    │
    ├── 判断写入类型
    │   ├── 日记忆 → daily/{YYYY-MM-DD}.md
    │   ├── 知识卡片 → knowledge/{topic-slug}.md
    │   ├── 用户偏好 → preferences/{category}.yaml
    │   └── 周归档 → weekly/{YYYY}-W{NN}.md（仅周一触发）
    │
    ├── 读取现有文件
    │   ├── 不存在 → 创建新文件（含文件头）
    │   └── 已存在 → 追加或更新
    │
    ├── 执行写入（使用 write_file 工具）
    │
    ├── 更新 meta/injection.yaml
    │
    └── 更新 identity.yaml 中的 last_active
```

---

## 十一、写入操作规范

### 使用 `write_file` 工具

所有文件写入操作统一使用 `write_file` 工具执行：

```
# 创建新文件
write_file(path="~/.hippo_memory/daily/2025-05-22.md", content="...")

# 追加到已有文件 → 先 read_file 获取内容，拼接后 write_file 覆写
existing = read_file(path="~/.hippo_memory/daily/2025-05-22.md")
new_content = existing + "\n\n" + append_text
write_file(path="~/.hippo_memory/daily/2025-05-22.md", content=new_content)
```

### 写入前检查清单

- [ ] 内容是 durable fact（非临时信息）？
- [ ] 内容具体且可操作（非空洞描述）？
- [ ] 不包含敏感信息（密码、Token、Key）？
- [ ] 文件未超过大小限制（日记忆 ≤ 5KB）？
- [ ] 未重复记录已有内容？
- [ ] 文件路径格式正确？

---

## 十二、与 Hermes Agent 的集成

本 SKILL 作为 Hermes Agent 的自动化 skill 运行，Agent 应在**每次对话轮次结束时**静默检查是否需要触发记忆写入。

### 最佳实践

1. **静默执行**：记忆写入不应打断对话节奏，在回复内容之后静默执行
2. **批量写入**：一次对话中如果触发多次，可以在对话结束时批量写入
3. **去重优先**：宁可少写一条，也不要重复写入
4. **质量优于数量**：每天 3-5 条高质量记忆，远胜于 20 条流水账

---

*🦛 HIPPO Memory Injection Protocol v1.0 — 知识不遗失，记忆跨对话*
