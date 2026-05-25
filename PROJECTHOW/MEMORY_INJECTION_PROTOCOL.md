# HIPPO Memory Injection Protocol (记忆注入协议)

> **文档版本**: v1.0 Draft  
> **创建日期**: 2026-05-22  
> **作者**: 赫墨 + 鱼总  
> **状态**: 设计阶段  
> **注册编号**: 待分配（registry.yaml）

---

## 0. 一句话

> **HIPPO 不是备份工具——它是"让 Agent 拥有持久记忆的软件"。**

---

## 1. 问题定义

### 1.1 现状

```
用户有 Agent（Hermes / OpenClaw / Claude / ……）
  → Agent 每天产生大量对话、操作、知识
  → 但 Agent 默认不保存结构化记忆文件
  → HIPPO 扫描时发现：没什么可复制的
  → 产品价值大打折扣
```

### 1.2 根因

AI Agent 的记忆机制各不相同：

| Agent | 内建记忆 | 持久化方式 | 用户可控性 |
|-------|---------|-----------|-----------|
| Hermes | `memory` 工具（~2200字符内联） | 自动注入每轮对话 | 中等 |
| OpenClaw | `MEMORY.md` / `memory/` 目录 | 文件系统 | 高 |
| Claude Code | `CLAUDE.md` + `memory` 工具 | 项目级文件 | 中等 |
| 通用 Agent | 无 | 无 | 低 |

**核心矛盾**：Agent 有记忆能力，但**没有记忆习惯**。用户不知道要让 Agent 定期保存什么、保存到哪里、用什么格式。

### 1.3 解决方案

```
HIPPO 提供「记忆注入协议」→ 注入到用户的 Agent → 
Agent 开始定期产生结构化记忆文件（日压缩 / 周归档）→ 
HIPPO 的规则扫描才有内容可抓 → 
用户发现记忆有价值 → 更依赖 HIPPO → 续费
```

**这是一个「创造供给 → 创造需求」的闭环。**

---

## 2. 协议设计

### 2.1 标准记忆文件格式

HIPPO 定义一个 **Agent 无关**的标准记忆目录和文件格式：

```
~/.hippo_memory/                         ← 标准记忆根目录（所有 Agent 共用）
├── identity.yaml                        ← Agent 身份卡
├── daily/                               ← 日记忆（每天一份）
│   ├── 2026-05-22.md
│   ├── 2026-05-21.md
│   └── ...
├── weekly/                              ← 周归档（每周一份压缩摘要）
│   ├── 2026-W21.md
│   └── ...
├── knowledge/                           ← 知识卡片（按主题归档）
│   ├── finance-macro.md
│   ├── devops-docker.md
│   └── ...
├── preferences/                         ← 用户偏好（Agent 学习到的）
│   ├── communication-style.md
│   ├── coding-conventions.md
│   └── ...
└── meta/
    └── injection.yaml                   ← 注入元数据（版本、时间戳）
```

#### 2.1.1 identity.yaml（Agent 身份卡）

```yaml
# HIPPO Memory Protocol — Agent Identity Card
agent_name: "Hermes"                      # Agent 名称
agent_version: "2.x"                      # Agent 版本
user_name: "Gabriel"                      # 用户名
injection_protocol: "1.0"                 # 协议版本
created_at: "2026-05-22T07:30:00+08:00"   # 首次注入时间
last_updated: "2026-05-22T19:00:00+08:00" # 最后更新时间
memory_schedule: "daily"                  # 压缩周期: daily / weekly / manual
agent_platform: "hermes"                  # 平台标识（hermes/openclaw/claude/generic）
```

#### 2.1.2 日记忆文件格式（daily/*.md）

```markdown
# 记忆日志 — 2026-05-22

## 📌 今日关键决策
- [决策1] 决定使用 PyQt6 替代 Streamlit 作为 GUI 框架
- [决策2] 授权系统采用 HMAC-SHA256 激活码方案

## 🔧 技术发现
- Windows 版 PyQt6 wheel 下载需用清华镜像（6.6M+75M+53K）
- WSL interop 在 exec driver 模式下不可用，需降级处理

## ⚠️ 纠正与教训
- 鱼总纠正：入口文件必须叫 Hippocampus，不叫 autorun
- 不应该用浏览器 Web UI 作为产品默认界面

## 📋 待跟进
- [ ] 授权系统 Phase 1 实现
- [ ] 记忆注入协议设计文档
- [ ] U盘烧录测试

## 🧠 知识沉淀
- Docker Hub 被墙 → 用 GHCR
- arxiv / raw.githubusercontent.com 中国不可达 → API fallback
```

#### 2.1.3 周归档格式（weekly/*.md）

```markdown
# 周归档 — 2026-W21 (05-19 ~ 05-25)

## 本周主题
- HIPPO v4.0.0 跨平台兼容性修复

## 关键事件时间线
| 日期 | 事件 |
|------|------|
| 05-19 | 雄安新区区域报告交付 |
| 05-20 | Streamlit 移除，PyQt6 GUI 重构 |
| 05-21 | Windows Hippocampus.bat 双模式入口 |
| 05-22 | 记忆注入协议设计启动 |

## 本周纠正（重要）
1. GUI 不能用浏览器 → 必须原生桌面
2. 入口不能叫 autorun → 叫 Hippocampus
3. 不改底层代码（除非用户明确要求）

## 累积知识
- [链接到 knowledge/ 下的对应文件]

## 下周计划
- 授权系统实现
- 记忆注入协议落地
```

#### 2.1.4 知识卡片格式（knowledge/*.md）

```markdown
# 知识卡片：finance-macro

## 元数据
- 主题：宏观经济分析
- 创建：2026-05-22
- 累计引用：3次
- 最后更新：2026-05-22

## 核心知识点
1. 央行降准对债券市场的传导机制
2. PMI 走势与 A 股行业轮动的关系
3. ...

## 相关对话索引
- session:2026-05-19_xxxx → 雄安新区经济数据分析
- session:2026-05-20_yyyy → 量化因子讨论

## 已验证来源
- [1] 新华社官方发布
- [2] xiongan.gov.cn 统计公报
```

#### 2.1.5 偏好文件格式（preferences/*.md）

```markdown
# 用户偏好：communication-style

## 沟通风格
- 中文为主，英文/西语为辅
- 效率至上：能一步完成不要三步
- 幽默轻松日常，关键时刻严肃
- 路径整洁癖：不重复存放，不嵌套冗余

## 技术偏好
- 先定义术语再使用
- 不说"在忙"，说技术原因
- 收到多主题任务立即拆解并行执行
```

### 2.2 注入方式

记忆注入协议的核心是：**把"记忆习惯"植入 Agent 的运行时行为中**。

不同 Agent 平台的注入方式：

| 平台 | 注入方式 | 注入物 | 触发时机 |
|------|---------|-------|---------|
| **Hermes** | `memory` 工具 + SKILL 注入 | `hippo-memory-skill` SKILL.md | Agent 启动时自动加载 |
| **OpenClaw** | Prompt 模板注入 | `hippo-memory-prompt.md` | 用户配置 workspace |
| **Claude Code** | `CLAUDE.md` 片段 | hippo-memory 片段 | 项目级自动加载 |
| **通用 Agent** | 用户手动引导 | 转载到 Agent 对话 | 用户主动触发 |

### 2.3 注入模板

详见以下独立文件：
- `templates/hermes-skill-SKILL.md` — Hermes SKILL 模板
- `templates/openclaw-prompt.md` — OpenClaw prompt 注入模板
- `templates/generic-agent-prompt.md` — 通用 Agent 对话引导模板

---

## 3. HIPPO 扫描端对接

### 3.1 ai_tools.yaml 扩展

在现有 `ai_tools.yaml` 中新增 `hippo_memory` 工具条目：

```yaml
  # ========== HIPPO 标准记忆 ==========
  - name: "hippo_memory"
    display_name: "HIPPO Memory Protocol"
    enabled: true
    priority: highest                    # 最高优先级
    description: "HIPPO 记忆注入协议产生的标准记忆文件"
    paths:
      - path: "~/.hippo_memory/"
        type: "directory"
        description: "HIPPO 标准记忆根目录"
      - path: "~/.hippo_memory/daily/*.md"
        type: "glob"
        description: "日记忆文件"
      - path: "~/.hippo_memory/weekly/*.md"
        type: "glob"
        description: "周归档文件"
      - path: "~/.hippo_memory/knowledge/*.md"
        type: "glob"
        description: "知识卡片"
      - path: "~/.hippo_memory/preferences/*.md"
        type: "glob"
        description: "用户偏好"
```

### 3.2 rules_engine.py 扩展

在 `RulesEngine._load_default_rules()` 中新增 HIPPO 记忆规则（**最高置信度**）：

```python
# HIPPO 记忆协议 — 最高置信度
self.rules.append(Rule(
    name="hippo_daily_memory",
    path_pattern="~/.hippo_memory/daily/**/*.md",
    confidence=Confidence.HIGH,
    source="hippo_memory"
))
self.rules.append(Rule(
    name="hippo_weekly_archive",
    path_pattern="~/.hippo_memory/weekly/**/*.md",
    confidence=Confidence.HIGH,
    source="hippo_memory"
))
self.rules.append(Rule(
    name="hippo_knowledge_cards",
    path_pattern="~/.hippo_memory/knowledge/**/*.md",
    confidence=Confidence.HIGH,
    source="hippo_memory"
))
self.rules.append(Rule(
    name="hippo_preferences",
    path_pattern="~/.hippo_memory/preferences/**/*.md",
    confidence=Confidence.HIGH,
    source="hippo_memory"
))
self.rules.append(Rule(
    name="hippo_identity",
    path_pattern="~/.hippo_memory/identity.yaml",
    confidence=Confidence.HIGH,
    source="hippo_memory"
))
```

### 3.3 扫描优先级

```
HIPPO 标准记忆（~/.hippo_memory/）     → 最高置信度 HIGH
  ↓ 降级
Agent 原生记忆（~/.hermes/, ~/.openclaw/）→ 中置信度 MEDIUM  
  ↓ 降级
通用 Markdown 匹配                      → 低置信度 LOW
```

**设计意图**：HIPPO 注入的记忆文件格式是确定的、结构化的，扫描匹配应该最精确。

---

## 4. 闭环验证

### 4.1 完整闭环

```
                    ┌──────────────────────┐
                    │   HIPPO 注入协议 v1.0 │
                    │ (SKILL / Prompt 模板) │
                    └──────────┬───────────┘
                               │ 注入
                               ▼
                    ┌──────────────────────┐
                    │     Agent 运行时      │
                    │ 产生结构化记忆文件     │
                    │ (daily/weekly/know)   │
                    └──────────┬───────────┘
                               │ 写入
                               ▼
                    ┌──────────────────────┐
                    │  ~/.hippo_memory/     │
                    │  标准记忆目录          │
                    └──────────┬───────────┘
                               │ 扫描
                               ▼
                    ┌──────────────────────┐
                    │  HIPPO Scanner v4.0   │
                    │  ai_tools.yaml 检测   │
                    │  rules_engine 匹配    │
                    └──────────┬───────────┘
                               │ 备份
                               ▼
                    ┌──────────────────────┐
                    │  U盘 / 本地备份       │
                    │  用户发现记忆有价值     │
                    └──────────┬───────────┘
                               │ 续费
                               ▼
                    ┌──────────────────────┐
                    │  HIPPO 商业闭环 ✅     │
                    └──────────────────────┘
```

### 4.2 验证清单

- [ ] `~/.hippo_memory/` 目录能被 scanner.py 的 `scan_all()` 发现
- [ ] `ai_tools.yaml` 中 `hippo_memory` 条目优先级为 highest
- [ ] `rules_engine.py` 新增 HIPPO 规则后，日记忆文件匹配置信度为 HIGH
- [ ] Hermes SKILL 加载后，Agent 能自动写日记忆到 `~/.hippo_memory/daily/`
- [ ] OpenClaw prompt 注入后，Agent 能识别并执行记忆写入指令
- [ ] 完整闭环跑通：注入 → 产生 → 扫描 → 备份

---

## 5. 商业价值

### 5.1 为什么记忆注入是护城河

| 维度 | 没有注入协议 | 有注入协议 |
|------|------------|-----------|
| 产品定位 | "AI 记忆备份工具" | "让 Agent 拥有持久记忆的软件" |
| 用户粘性 | 低（备份完就忘了） | 高（Agent 天天产生记忆，天天需要备份） |
| 可替代性 | 高（任何文件同步工具都能做） | 低（记忆格式是 HIPPO 定义的） |
| 网络效应 | 无 | 有（Agent 越多 → 记忆越多 → 越离不开） |
| 定价权 | 弱 | 强（记忆价值随时间递增） |

### 5.2 竞争壁垒

1. **格式标准**：`~/.hippo_memory/` 成为事实标准
2. **生态锁定**：Agent 的记忆习惯由 HIPPO 塑造
3. **数据累积**：备份越多，迁移成本越高
4. **先发优势**：目前市场上没有同类产品

### 5.3 三个"第一次"

1. **第一次**定义 AI Agent 的标准记忆文件格式
2. **第一次**把"让 Agent 有记忆习惯"做成产品功能
3. **第一次**实现 Agent 记忆的「注入 → 产生 → 备份 → 价值」闭环

---

## 6. 版本规划

| 阶段 | 版本 | 内容 | 状态 |
|------|------|------|------|
| Phase 0 | v1.0 设计文档 | 协议定义 + 模板设计 | ✅ 本文档 |
| Phase 1 | v1.1 模板实现 | Hermes SKILL + OpenClaw prompt + 通用模板 | 待开发 |
| Phase 2 | v1.2 扫描对接 | ai_tools.yaml + rules_engine 扩展 | 待开发 |
| Phase 3 | v1.3 GUI 集成 | HIPPO GUI 中显示注入状态和记忆统计 | 待开发 |
| Phase 4 | v1.4 自动注入 | U盘插入时自动检测 Agent 并注入 | 待开发 |

---

## 7. 术语表

| 术语 | 定义 |
|------|------|
| **记忆注入协议** | HIPPO 定义的规范，指导 Agent 如何产生结构化记忆文件 |
| **标准记忆目录** | `~/.hippo_memory/`，所有 Agent 共用的记忆文件存放位置 |
| **日记忆** | Agent 每天自动压缩生成的当日交互摘要 |
| **周归档** | Agent 每周自动生成的跨日压缩摘要 |
| **知识卡片** | Agent 从对话中提取的结构化知识单元 |
| **偏好文件** | Agent 学习到的用户习惯和偏好 |
| **注入物** | 用于注入到 Agent 的模板文件（SKILL / prompt / 对话引导） |
| **注入协议版本** | `injection.yaml` 中的 `injection_protocol` 字段，当前为 "1.0" |

---

## 附录

### A. 文件清单

```
PROJECTHOW/MEMORY_INJECTION_PROTOCOL.md          ← 本文档
PROJECTHOW/templates/
├── hermes-skill-SKILL.md                         ← Hermes SKILL 模板
├── openclaw-prompt.md                            ← OpenClaw prompt 注入模板
└── generic-agent-prompt.md                       ← 通用 Agent 对话引导模板
```

### B. 与现有系统的关系

```
记忆注入协议 ←→ HIPPO Scanner (ai_tools.yaml + rules_engine)
记忆注入协议 ←→ HIPPO GUI (注入状态显示)
记忆注入协议 ←→ HIPPO USB (自动注入功能)
记忆注入协议 ←→ AnswerSheet (记忆验证)
```

### C. 参考

- HIPPO Skill: `/home/agentuser/.hermes/skills/productivity/hippocampus/SKILL.md`
- 权限系统: `/mnt/x/CLABIN/HIPPO/PROJECTHOW/AUTH_SYSTEM_v1.md`
- 规则引擎: `/mnt/x/CLABIN/HIPPO/hippocampus-for-usb/brain_dump_linux/lib/rules_engine.py`
- AI工具配置: `/mnt/x/CLABIN/HIPPO/hippocampus-for-usb/brain_dump_linux/lib/config/ai_tools.yaml`
