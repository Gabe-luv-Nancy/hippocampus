# HIPPO V4 功能规划文档

> 起草：2026-04-20
> 状态：规划中，待 HIPPO 组分工确认

---

## 一、HIPPO 双版本结构（现状）

```
hippocampus-for-github/          ← GitHub 全代码版（完整交付）
│
├── SKILL.md                    ← OpenClaw Skill 定义（prompt 注入）
├── skill.yaml                  ← Skill 元数据
├── VERSION                     ← 版本号（当前：3.0.0）
├── USER_CONFIG.md              ← 用户配置（YAML 格式）
│
├── scripts/                    ← 核心 Python 模块
│   ├── memory.py               ← 双存储引擎（Chronicle + Monograph）
│   ├── scanner.py              ← 文件扫描引擎
│   ├── detector.py             ← AI 工具检测
│   ├── rules_engine.py         ← 规则匹配引擎
│   ├── usb_detector.py         ← U 盘检测
│   ├── streamlit_app.py        ← Web UI
│   └── config/
│       ├── ai_tools.yaml       ← AI 工具路径库
│       └── scan_rules.yaml     ← 扫描规则
│
├── gui/                        ← PyQt6 桌面 GUI
│   ├── gui_main.py
│   ├── app.py
│   └── utils/
│       ├── backup_engine.py
│       ├── drive_detector.py
│       └── styles.py
│
├── frontend/                   ← 前端资源（v3.1 遗留）
├── ui/local/                   ← UI 局部文件（v3.1 遗留）
└── assets/hippocampus/         ← 数据目录（运行时生成）
    ├── chronicle/              ← 时序记忆（SQLite + MD）
    ├── monograph/              ← 专题记忆
    └── index/                 ← 关键词索引

hippocampus-for-clawhub/         ← ClawHub 文本版（轻量分发）
├── CLAWHUB.yaml               ← ClawHub 元数据
├── PROMPT.md                  ← Prompt 内容（用户安装时读取）
└── SPEC.md                    ← 规格说明
```

**两版本关系：**
- `hippocampus-for-clawhub/PROMPT.md` = `hippocampus-for-github/SKILL.md` 的 prompt 段落（instruction 字段）
- ClawHub 用户通过 PROMPT.md 安装，不带任何 Python 代码

---

## 二、新功能一：Schema（结构化任务填表）

### 2.1 目标

在 HIPPO 的「任务填写」场景中，引入 YAML Schema 校验机制：
- AI 写入任务条目时，强制校验字段格式
- 不合格 → 写入拒绝 + 错误提示
- 做到「格式一致、打钩可验证」

### 2.2 核心机制（零依赖）

**Prompt 注入**（写进 SKILL.md 的 instruction 字段）：

```
## Schema 填写规范

写入 registry.yaml 时必须遵守：

字段规则：
| 字段 | 必填 | 取值 |
|------|------|------|
| id | ✅ | TASK-YYYYMMDD-NNN |
| title | ✅ | 字符串，≤100字 |
| status | ✅ | pending / in_progress / done |
| assignee | ✅ | ddb / ssm / fdm / test / ran / fep / bes |
| file_refs | ❌ | 列表，每项含 path + verified |
| file_refs[].path | ✅ | 真实文件路径 |
| file_refs[].verified | ❌ | 默认 false |

打钩规则：
status=done 前，必须所有 file_refs[].verified=true
```

### 2.3 实施清单

| 版本 | 新增文件 | 修改文件 |
|------|---------|---------|
| **github** | `scripts/task_schema/schema_models.py`（Pydantic 模型，可选） | `scripts/memory.py`（增加 checkpoint 时调用校验） |
| **github** | `scripts/task_schema/registry.py`（YAML 读写接口） | `scripts/memory.py` |
| **github** | `scripts/task_schema/validator.py`（纯标准库校验器） | `scripts/task_schema/README.md` |
| **github** | `scripts/task_schema/registry.yaml`（任务总表） | — |
| **github** | `scripts/task_schema/TASK_EXAMPLE.yaml`（示例条目） | — |
| **clawhub** | — | `PROMPT.md`（追加 Schema 规范段落） |

### 2.4 打钩验证逻辑

```
AI: 写入 status=done
        ↓
   Schema 校验层
        ↓
  ├─ 所有 file_refs[].verified == true?
  │     └─ 否 → 拒绝写入，返回错误
  └─ file_refs[].path 文件存在?
        └─ 否 → 路径错误提示
        ↓
   通过 → 写入成功 → status=done ✓
```

---

## 三、新功能二：Auto-Extract File Memory（自动记忆提取）

### 3.1 目标

对比「官方代码结构骨架」和「用户实际 Agent 形成的记忆文件」，自动识别：
- 用户通过 AI 指导新形成的 `.md` / `.yaml` / `.json` 等记忆文件
- 将这些文件备份到 HIPPO 的 Monograph 层
- 做到：换机器、换 Agent 版本 → 不丢失任何人类可读的记忆

### 3.2 核心思路

**创建两个路径数据库：**

```
SCHEMA_DIR = assets/hippocampus/schema/
│
├── base_schema.yaml          ← 官方骨架（版本固定，不含实际文件）
│   # 内容：所有官方路径的列表（固定不变）
│   paths:
│     - ~/.openclaw/workspace/MEMORY.md
│     - ~/.openclaw/workspace/SOUL.md
│     - ~/.openclaw/workspace/AGENTS.md
│     - ~/.openclaw/workspace/skills/*/SKILL.md
│     # ... 更多官方路径
│
└── user_schema.yaml          ← 用户实际路径（动态生成，每次扫描更新）
    # 内容：用户实际存在的所有路径
    paths:
      - ~/.openclaw/workspace/memory/2026-04-19.md
      - ~/.openclaw/workspace/MY_PROJECT_TODO.yaml
      - ~/.openclaw/workspace/PROJECT_X/notes.md
```

**比较逻辑：**

```
扫描用户目录 → 生成 user_schema.yaml
          ↓
    比对 base_schema.yaml
          ↓
    差异 = base_schema.yaml 中没有的路径
          ↓
    分类处理：
    ├─ 同名文件有更新 → 时间戳备份（如 model.json → model_20260420.json）
    └─ 全新文件名 → 复制到 assets/hippocampus/monograph/file_memory/
```

### 3.3 备份策略

| 文件类型 | 处理方式 |
|---------|---------|
| `model.json` / `config.yaml` 等**同名配置文件** | 加时间戳备份（不覆盖原历史） |
| `notes.md` / `TODO.md` / `REF_*.md` 等**独立文件名** | 直接复制到 `monograph/file_memory/` |

### 3.4 实施清单

| 版本 | 新增文件 | 修改文件 |
|------|---------|---------|
| **github** | `scripts/auto_extract/extract_schema.py`（路径对比引擎） | `scripts/memory.py`（增加 auto_extract 命令） |
| **github** | `scripts/auto_extract/base_schema.yaml`（官方骨架，版本化） | `scripts/auto_extract/README.md` |
| **github** | `scripts/auto_extract/extract_runner.py`（入口脚本） | `scripts/task_schema/registry.yaml`（Schema 示例） |
| **github** | `scripts/auto_extract/schema_generator.py`（扫描用户目录，生成 user_schema.yaml） | — |
| **github** | `scripts/auto_extract/backup_engine.py`（差异备份 + 时间戳命名） | — |
| **clawhub** | — | `PROMPT.md`（追加 auto_extract 说明） |

### 3.5 注意事项

- **完全不改用户配置**：只读，不写用户文件
- **备份目标**：HIPPO 自己的 `assets/hippocampus/monograph/file_memory/` 目录
- **触发方式**：cron 定时 或 AI 指令 `/hippo extract`

---

## 四、功能开发顺序

```
Phase 1: Schema（V4.1）
  └─ 建档 + 最小实现
  └─ github: schema_models + registry + validator
  └─ clawhub: PROMPT.md 追加

Phase 2: Auto-Extract File Memory（V4.2）
  └─ base_schema.yaml 建立（官方路径骨架）
  └─ schema_generator.py（用户路径扫描）
  └─ extract_runner.py + backup_engine.py

Phase 3: 集成（V4.3）
  └─ memory.py 集成 Schema 校验
  └─ memory.py 集成 auto_extract 命令
  └─ 双版本同步发布
```

---

## 五、HIPPO 组 Programmer 分工（待确认）

| 程序员 | 职责 |
|-------|------|
| **fep** | 前端 + 交互：Schema YAML 编辑器 UI（Streamlit / PyQt）、registry 可视化 |
| **bes** | 后端 + 运维：schema_models.py、validator.py、extract_runner.py、CI 校验脚本 |
| **ran** | 研究 + 规划：base_schema.yaml（官方路径骨架梳理）、auto_extract 规则定义、backup 策略研究 |

---

## 六、当前状态

| 项目 | 状态 |
|------|------|
| 本文档 | ✅ 起草完成，待讨论 |
| 双版本结构梳理 | ✅ 完成 |
| Schema 功能规划 | ✅ 完成 |
| Auto-Extract 功能规划 | ✅ 完成 |
| Programmer 分工 | ⬜ 待确认 |
| 开发任务派发 | ⬜ 待分工确认后执行 |

---

*本文档由 ED 维护，HIPPO 组 programmer 不许自行删除或移走。*
