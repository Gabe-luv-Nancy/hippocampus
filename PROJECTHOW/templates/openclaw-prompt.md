# HIPPO 记忆注入协议 — OpenClaw 配置

> **版本**: v1.0  
> **适用**: OpenClaw Agent（粘贴至 `MEMORY.md`、`SOUL.md` 或 `AGENTS.md` 中即可生效）

---

## 这是什么？

HIPPO（High-priority Injected Persistent Protocol Organizer）是一个跨 Agent 的**记忆注入与持久化协议**。它让你在与 OpenClaw 的对话过程中，将关键信息以结构化方式写入本地文件系统，形成持久化的"长期记忆"。

**为什么需要它？**
- 对话上下文有限，重要信息容易丢失
- 跨会话、跨 Agent 复用知识
- 形成可追溯的决策日志和技术知识库

---

## 记忆写入规则

### 目录结构

```
~/.hippo_memory/
├── identity.yaml          # 身份与偏好档案
├── daily/
│   ├── 2026-05-22.md      # 日记忆文件
│   └── ...
├── decisions/             # 关键决策归档
├── discoveries/           # 技术发现归档
└── followups/             # 待跟进事项
```

### 日记忆格式

每日记忆文件路径：`~/.hippo_memory/daily/{YYYY-MM-DD}.md`

文件内容使用以下 Markdown 模板：

```markdown
# 📅 {YYYY-MM-DD} 记忆日志

## 🔑 关键决策
<!-- 记录今天做出的重要选择及原因 -->
- **[决策标题]**: 描述 | 原因: xxx | 影响范围: xxx

## 🔬 技术发现
<!-- 记录新学到的技术知识、工具用法、踩坑经验 -->
- **[发现标题]**: 描述 | 来源: xxx | 验证状态: ✅/⚠️/❌

## 🔄 纠正记录
<!-- 记录之前的错误认知或做法的修正 -->
- **[纠正项]**: 旧认知 → 新认知 | 触发原因: xxx

## 📋 待跟进
<!-- 记录需要后续处理的事项 -->
- **[事项]**: 描述 | 优先级: P0/P1/P2 | 截止: YYYY-MM-DD

## 📚 知识沉淀
<!-- 记录值得长期保留的知识片段 -->
- **[知识标题]**: 内容摘要 | 标签: #tag1 #tag2
```

### 写入时机

当对话中出现以下情况时，**主动写入记忆**：

| 触发条件 | 写入类别 | 优先级 |
|---------|---------|-------|
| 用户明确做出技术选型/架构决定 | 关键决策 | 高 |
| 发现新工具、新 API、新解决方案 | 技术发现 | 高 |
| 纠正了之前的错误理解 | 纠正记录 | 高 |
| 用户提到"记住这个"、"下次别忘了" | 知识沉淀 | 高 |
| 有未完成的任务或待验证的假设 | 待跟进 | 中 |
| 调试过程中发现非显而易见的问题 | 技术发现 | 中 |

---

## identity.yaml 初始化指令

首次启用 HIPPO 协议时，在 `~/.hippo_memory/identity.yaml` 中创建用户身份档案：

```yaml
# HIPPO Identity — 用户身份与偏好档案
version: "1.0"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"

profile:
  name: ""           # 用户称呼（可选）
  role: ""           # 职业/角色（可选）
  timezone: ""       # 时区，如 Asia/Shanghai

preferences:
  language: "zh-CN"           # 默认交互语言
  code_style: ""              # 编码风格偏好
  framework_preference: []    # 偏好的框架/工具
  avoid: []                   # 明确不想要的工具/方案

context:
  current_projects: []        # 当前活跃项目
  tech_stack: []              # 常用技术栈
  key_directories: {}         # 项目目录映射

rules:
  auto_write_memory: true     # 是否自动写入记忆
  max_daily_file_kb: 32       # 单日记忆文件大小上限（KB）
  retention_days: 90          # 记忆保留天数
```

**初始化流程**：
1. 检查 `~/.hippo_memory/` 目录是否存在，不存在则创建
2. 检查 `identity.yaml` 是否存在，不存在则以默认值创建
3. 如用户在场，可主动询问补充 profile 信息

---

## OpenClaw 双写机制

为确保记忆在 OpenClaw 生态中不丢失，执行**双写**：

1. **主写入** → `~/.hippo_memory/` （HIPPO 标准目录，跨 Agent 共享）
2. **备份写入** → `~/.openclaw/workspace/memory/` （OpenClaw 原生记忆目录）

备份文件命名规则：`hippo-{YYYY-MM-DD}.md`

> **注意**：OpenClaw 原生记忆目录下的文件仅作备份参考，以 `~/.hippo_memory/` 中的内容为权威版本。

---

## 注意事项

### ✅ 应该记录的
- 用户明确表达的偏好和决策
- 经验证的技术方案和参数
- 踩坑经验及解决方案
- 项目上下文和架构决策

### ❌ 不应该记录的
- 临时性的试错过程（除非有教训价值）
- 明显的常识信息
- 敏感信息（密码、密钥、Token）
- 与用户项目无关的闲聊内容

### 文件大小控制
- 单日记忆文件不超过 **32KB**
- 超过时优先保留"关键决策"和"纠正记录"，精简"技术发现"
- 定期归档超过 90 天的日记忆到 `decisions/` 等分类目录

---

## 快速启动

将本段内容完整粘贴到以下任一文件中即自动生效：

- `~/.openclaw/workspace/MEMORY.md`
- `~/.openclaw/workspace/SOUL.md`
- `~/.openclaw/workspace/AGENTS.md`

粘贴后，下次对话中 OpenClaw 将自动遵循 HIPPO 协议进行记忆管理。

---

*HIPPO Protocol v1.0 — 让记忆跨越会话，让知识持久沉淀。*
