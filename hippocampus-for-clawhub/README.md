# Hippocampus REVELARE（ClawHub 版）

> **v4.0.0** | AI 增强记忆系统 — 提示词注入，AI 自动部署
> 作者：GabetopZ | License：MIT

---

## 核心理念

人类记忆天生有缺陷：**会遗忘、会扭曲、无法精确检索**。

Hippocampus 的哲学：**用 AI 修复这些缺陷，而不是模仿人类的遗忘机制。**

传统记忆系统使用衰减公式（0.99^days）——这是错的。AI 永远不会忘记。这才是重点。

---

## 功能一览

| 功能 | 版本 | 说明 |
|------|------|------|
| 🔥 **Schema — AI 任务进度表** | v4.0 | 任务标记完成前必须证明文件存在，AI 无法作弊 |
| 🔍 **AI 工具自动发现** | v3.0+ | 自动检测 12+ 款 AI 工具及其记忆文件 |
| 📦 **全覆盖备份引擎** | v3.0+ | SHA256 增量备份，双端日志完全可追溯 |
| 🧠 **双层记忆系统** | v1.0 | Chronicle（事件流）+ Monograph（主题） |
| ⏰ **定时自动保存** | v2.0+ | Cron 任务自动运行，无需手动操作 |
| ⚠️ **失败模式预警** | v3.0+ | 检测失败模式，在重蹈覆辙前主动警告 |
| 📂 **Auto-Extract 文件记忆** | v4.2 | 自动识别用户新形成的记忆文件并备份 |
| 🖥️ **PyQt6 GUI** | v3.1 | 本地模式 + USB 模式图形界面 |
| 🌐 **Streamlit Web UI** | v3.0 | 浏览器访问的记忆管理界面 |

---

## 目录结构

```
hippocampus-for-clawhub/
├── CLAWHUB.yaml               # ClawHub 平台元数据（名称、版本、触发词等）
├── PROMPT.md                  # AI 部署指令（核心文件）
├── SKILL.md                   # ClawHub Skill 定义（AI 运行时读取）
├── README.md                  # 本文档
├── gui_main.py                # PyQt6 GUI 入口（644 行）
├── gui/                       # GUI 模块
│   ├── __init__.py
│   ├── app.py                 # 主窗口与交互逻辑（185 行）
│   └── utils/
│       ├── __init__.py
│       ├── backup_engine.py   # GUI 备份引擎（353 行）
│       ├── drive_detector.py  # 驱动器检测（204 行）
│       └── styles.py          # 样式定义（216 行）
└── scripts/                   # 核心脚本
    ├── memory.py              # 核心记忆引擎（1366 行）
    ├── detector.py            # AI 工具自动发现（314 行）
    ├── scanner.py             # 全覆盖备份引擎（495 行）
    ├── rules_engine.py        # 规则匹配引擎（387 行）
    ├── usb_detector.py        # USB 检测（364 行）
    ├── streamlit_app.py       # Streamlit Web UI（721 行）
    ├── config/                # 配置文件
    │   ├── ai_tools.yaml      # AI 工具识别规则
    │   └── scan_rules.yaml    # 扫描规则
    ├── task_schema/           # Schema AI 任务进度表
    │   ├── schema_models.py   # 数据模型（68 行）
    │   ├── validator.py       # 规则引擎（73 行）
    │   ├── registry.py        # YAML 读写接口（115 行）
    │   └── registry.yaml      # 任务注册表
    └── auto_extract/          # 文件记忆自动提取
        ├── __init__.py
        ├── backup_engine.py   # 备份引擎（43 行）
        ├── extract_runner.py  # 提取运行器（95 行）
        ├── schema_generator.py # Schema 生成器（119 行）
        ├── base_schema.yaml   # 基础 Schema 模板
        └── user_schema.yaml   # 用户自定义 Schema
```

**总代码量：~5765 行**

---

## 快速使用（怎么用）

### 用户安装：在 ClawHub 中一键安装

```bash
openclaw skill install hippocampus
```

安装完成后，AI 会自动读取 `PROMPT.md` 并执行完整部署流程（创建目录 → 复制脚本 → 生成元数据 → 初始化数据库 → 验证可用性）。

### 手动安装

```bash
git clone https://github.com/Gabe-luv-Nancy/hippocampus.git hippocampus-for-clawhub
cd hippocampus-for-clawhub
python3 scripts/memory.py init
python3 scripts/memory.py status
```

### 安装后验证

```bash
python3 scripts/memory.py status
```

预期输出：显示 Chronicle 和 Monograph 状态，记录数为 0。

### 基本命令

| 命令 | 说明 |
|------|------|
| `/photon status` | 查看记忆状态 |
| `/photon save` | 保存当前上下文 |
| `/photon recall <keyword>` | 精确召回 |
| `/photon checkpoint` | 保存项目状态 |
| `/photon warn` | 检查失败模式 |
| `/photon schema list` | 查看 Schema 任务表 |
| `/photon schema check <task_id>` | 验证指定任务 |
| `/hippo extract --dry-run` | 预览新文件扫描结果 |
| `/hippo extract` | 执行文件记忆备份 |

### 底层脚本命令

```bash
python3 scripts/memory.py init                # 初始化（首次必须运行）
python3 scripts/memory.py status              # 查看记忆状态
python3 scripts/memory.py recall <keyword>    # 精确召回
python3 scripts/scanner.py scan               # 全覆盖 AI 工具扫描
python3 scripts/scanner.py scan --usb <path>  # USB 备份扫描
python3 scripts/detector.py                   # 检测已安装 AI 工具
python3 scripts/task_schema/registry.py list       # 查看所有任务
python3 scripts/task_schema/registry.py get <id>   # 查看单个任务
python3 scripts/task_schema/validator.py check <id> # 验证任务状态
python3 gui_main.py --mode local              # 启动本地 GUI
```

### 触发关键词

当用户在对话中使用以下关键词时，AI 会自动激活 Hippocampus 功能：

`remember` · `recall` · `checkpoint` · `memory` · `schema` · `task` · `registry` · `progress` · `where did we leave off` · `what was i working on` · `warn me about`

---

## 发布指南（怎么发布）

### ClawHub Skill 发布流程

1. **准备发布包**：确保 `hippocampus-for-clawhub/` 目录包含所有必需文件
   - `CLAWHUB.yaml` — 平台元数据（名称、版本、描述、触发词等）
   - `PROMPT.md` — AI 部署指令（核心部署流程）
   - `SKILL.md` — Skill 定义（AI 读取的指令文件）
   - `scripts/` — 完整 Python 脚本
   - `gui/` — GUI 模块
   - `gui_main.py` — GUI 入口

2. **更新版本号**：同步修改以下位置
   - `CLAWHUB.yaml` 中 `version:` 字段
   - `SKILL.md` 中 `version:` 字段
   - `PROMPT.md` 中 `skill.yaml` 和 `SKILL.md` 模板里的版本号
   - `README.md` 头部版本标记

3. **提交到 ClawHub**：
   ```bash
   openclaw skill publish hippocampus
   ```

4. **验证发布**：
   ```bash
   openclaw skill search hippocampus
   ```

### PROMPT.md 更新规范

`PROMPT.md` 是 AI 自动部署的核心指令文件，更新时须遵循：

- **Step 编号连续**：部署步骤（Step 1 → Step N）必须连续、无跳跃
- **文件清单同步**：`scripts/` 目录下的文件变更必须反映在 PROMPT.md 的文件清单中
- **版本号一致**：所有模板中的版本号必须与 CLAWHUB.yaml 中版本一致
- **禁止外部依赖**：所有 Python 脚本仅使用 stdlib，不引入 pip 依赖
- **路径一致性**：安装目标路径固定为 `~/.openclaw/workspace/skills/hippocampus/`

### 版本同步流程

```
CLAWHUB.yaml version 更新
      ↓
SKILL.md version 同步
      ↓
PROMPT.md 中所有模板 version 同步
      ↓
README.md 头部版本标记同步
      ↓
提交发布
```

---

## 部署流程详解（AI 自动执行）

用户在 ClawHub 安装 Hippocampus 后，AI 自动读取 `PROMPT.md` 并按以下步骤执行部署：

### 部署步骤

```
用户: 安装 hippocampus
  ↓
AI 读取 PROMPT.md
  ↓
Step 1: 创建目录结构
        ~/.openclaw/workspace/skills/hippocampus/
        ├── scripts/
        ├── scripts/task_schema/
        ├── scripts/config/
        └── assets/hippocampus/{chronicle,monograph,index}/
  ↓
Step 2: 复制 scripts/ 到目标路径
  ↓
Step 3: 复制 gui_main.py 和 gui/
  ↓
Step 4: 生成 skill.yaml（元数据）
  ↓
Step 5: 生成 USER_CONFIG.md（用户配置模板）
  ↓
Step 6: 生成 README.md（用户文档）
  ↓
Step 7: 生成 SKILL.md（AI 指令文件）
  ↓
Step 8: 运行 python3 scripts/memory.py init
  ↓
Step 9: 验证 python3 scripts/memory.py status
  ↓
Step 10: 报告完成
```

### 安装目标路径

```
~/.openclaw/workspace/skills/hippocampus/
```

### 可选：定时任务

部署完成后可按需设置：

```bash
# 每 6 小时自动保存
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py autocheck"

# 每天 23:00 自动分析
openclaw cron add --name "hippocampus-analyze" \
  --schedule "0 23 * * *" --session-target isolated \
  --payload "Run: python3 ~/.openclaw/workspace/skills/hippocampus/scripts/memory.py analyze"
```

---

## 模块详解

### 核心引擎：memory.py（1366 行）

双层记忆架构的 Python 实现：

- **Chronicle**：按时间排列的事件流，线性记录每次交互
- **Monograph**：按主题聚合的知识卡片，支持精确检索
- 命令行接口：`init` / `status` / `recall` / `save` / `autocheck` / `analyze`

### AI 工具发现：detector.py（314 行）

自动扫描系统中已安装的 AI 工具及其记忆文件位置。支持 12+ 款工具，包括：

- Cursor · Windsurf · Claude Code · Codex · Cline · Aider · Continue 等
- 配置文件：`scripts/config/ai_tools.yaml`

### 备份引擎：scanner.py（495 行）

SHA256 增量备份，确保文件级别的完整追踪：

- 本地扫描模式 + USB 目标模式
- 双端日志（客户端 + USB 端）完全可追溯
- 配置文件：`scripts/config/scan_rules.yaml`

### 规则引擎：rules_engine.py（387 行）

模式匹配与失败预警：

- 加载自定义规则，检测重复失败模式
- 在用户重蹈覆辙前主动警告

### Schema 任务系统：task_schema/

v4.0 核心功能——AI 任务进度表，强制 AI 遵守规则并承担责任：

```
AI: "我想把任务 HIPPO-XXX 标记为完成"
        ↓
validator.py: "你所有的 file_refs[].verified=true 了吗？"
        ↓
AI: 验证每个文件路径 → 文件都存在才能标记完成
        ↓
验证不过就写不进去，没有讨价还价的余地。
```

| 文件 | 说明 |
|------|------|
| `schema_models.py` | 数据模型（68 行） |
| `validator.py` | 规则引擎——必须通过才能标记完成（73 行） |
| `registry.py` | YAML 读写接口（115 行） |
| `registry.yaml` | 任务注册表（AI 进度表） |

**Schema 验证规则：**
- `status=done` 要求所有 `file_refs[].verified=true`
- `verified=true` 要求文件路径实际存在于磁盘
- `depends_on` 依赖链：上游未完成 → 下游不可完成
- 任何 AI 都可查询任务表，准确定位阻塞点

### Auto-Extract：文件记忆自动提取

自动识别用户新形成的记忆文件并备份：

| 文件 | 说明 |
|------|------|
| `extract_runner.py` | 提取运行器（95 行） |
| `schema_generator.py` | Schema 生成器（119 行） |
| `backup_engine.py` | 备份引擎（43 行） |
| `base_schema.yaml` | 基础 Schema 模板 |
| `user_schema.yaml` | 用户自定义 Schema |

### GUI 模块

PyQt6 图形界面，支持本地模式和 USB 模式：

| 文件 | 说明 |
|------|------|
| `gui_main.py` | 入口脚本（644 行） |
| `gui/app.py` | 主窗口与交互逻辑（185 行） |
| `gui/utils/backup_engine.py` | GUI 备份引擎（353 行） |
| `gui/utils/drive_detector.py` | 驱动器检测（204 行） |
| `gui/utils/styles.py` | 样式定义（216 行） |

---

## AI 集成说明

### SKILL.md

`SKILL.md` 是 ClawHub 的 Skill 定义文件，AI 在运行时读取此文件获取指令。核心内容：

- **元数据**：name、version、description、author、license、tags、triggers
- **运行时模式**：`instruction-first`（指令优先）+ `code_on_demand: true`（按需执行代码）
- **权限**：read / write / exec
- **依赖**：python3 >= 3.8
- **指令内容**（instruction 字段）：完整的 AI 行为指南，包括功能描述、命令列表、触发关键词

### CLAWHUB.yaml

ClawHub 平台的 listing 元数据，定义安装方式和兼容性：

- `installation.type: prompt` — 通过提示词注入安装
- `installation.prompt_file: PROMPT.md` — 指定部署指令文件
- `compatibility` — 支持 Linux / macOS / Windows / WSL，OpenClaw >= 1.0.0

### 技术亮点

- **零外部依赖**：所有 Python 脚本仅使用 stdlib，无需 pip install
- **YAML 注册表**：Schema 使用纯 YAML 实现，无数据库依赖
- **跨平台**：支持 Linux / macOS / Windows / WSL
- **兼容性**：OpenClaw >= 1.0.0

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| Init 报错 "directory exists" | 检查目标路径是否有残留文件，清理后重试 |
| detector.py 报错 | 确认系统路径正确（Linux: ~/.config 或 ~/.local） |
| 权限错误 | 检查写入权限，执行 `chmod +x gui_main.py` |
| Schema 命令无响应 | 确认 task_schema/ 目录完整部署 |
| 版本不匹配 | 检查 CLAWHUB.yaml、SKILL.md、PROMPT.md 中版本号一致 |
| GUI 无法启动 | 确认已安装 PyQt6：`pip install PyQt6` |

---

## 版本历史

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| **v4.0.0** | 2026-04-22 | Schema AI 任务进度表，强制核销规则；双端日志；12+ AI 工具支持 |
| **v3.1.0** | 2026-03-25 | 命令统一为 `/hippo`；PyQt6 GUI；USB 预构建 SQLite |
| **v3.0.0** | 2026-02 | AI 工具自动发现；全覆盖备份引擎；规则匹配引擎 |
| **v2.0.0** | 2025 | 知识图谱；自动分析 + 关键词索引 |
| **v1.0.0** | 2024 | 双层记忆系统：Chronicle + Monograph；核心引擎 memory.py |

---

## License

MIT License © GabetopZ
