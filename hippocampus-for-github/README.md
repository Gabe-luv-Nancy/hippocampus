# Hippocampus SERVO（GitHub 版）

[![GitHub stars](https://img.shields.io/github/stars/Gabe-luv-Nancy/hippocampus)](https://github.com/Gabe-luv-Nancy/hippocampus/stargazers)
[![Version](https://img.shields.io/badge/version-4.0.0-blue)](https://github.com/Gabe-luv-Nancy/hippocampus)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **v4.0.0** | 别名 SERVO | 完整源码发行版
> "AI is meant to FIX human memory flaws, why learn human decay?"

---

## 核心理念

人类记忆天然有缺陷：**会遗忘、会扭曲、无法精确检索**。

Hippocampus 的理念是：**用 AI 修复这些缺陷，而不是模仿它们**。AI 从不遗忘，这才是重点。

| 人类记忆 | Hippocampus |
|---------|-------------|
| 遗忘 → | 永不遗忘 |
| 模糊匹配 → | 精确时间戳 |
| 被动触发 → | 主动预警 |
| 重要性衰减 → | 永久保留 |

**三版发行体系**：

| 版本 | 部署方式 | 别名 |
|------|---------|------|
| GitHub（本仓库） | `git clone` + 手动运行 | Hippocampus **SERVO** |
| Clawhub | 提示词注入，AI 自动部署 | Hippocampus **REVELARE** |
| BrainDump U 盘 | 直接复制到 U 盘 | Hippocampus **DATUM** |

---

## 功能一览

| # | 功能 | 说明 | 自版本 |
|---|------|------|--------|
| 1 | **Schema — AI 任务进度表** | 强制打钩机制：文件路径不存在就写不进去 done | v4.0 |
| 2 | **AI 工具自动发现** | 扫描主机检测已安装 AI 工具（OpenClaw/Kimi/豆包/DeepSeek 等 12+） | v3.0 |
| 3 | **全覆盖备份引擎** | SHA256 增量判断，两端日志对照可追溯 | v3.0 |
| 4 | **双层记忆系统** | Chronicle（事件流）+ Monograph（专题） | v1.0 |
| 5 | **Auto-Extract** | 自动识别用户通过 AI 新形成的记忆文件并备份 | v4.2 |
| 6 | **察言观色** | 高频词自动加载相关记忆 | v3.1 |
| 7 | **知识图谱** | Skill → Project → Goal 网状关联 | v2.0 |
| 8 | **自动保存** | Cron 定时任务，无需 session hooks | v2.0 |
| 9 | **图形界面** | PyQt6 桌面 + Streamlit Web 双 UI | v3.1 |

---

## 目录结构

```
hippocampus/
├── README.md                    ← 本文件（唯一文档，全覆盖）
├── VERSION                      ← 版本号（4.0.0）
├── LICENSE                      ← MIT
├── SKILL.md                     ← Skill 快速参考（命令/触发词）
├── USER_CONFIG.md               ← 用户配置说明
├── skill.yaml                   ← OpenClaw Skill 元数据
├── gui_main.py                  ← PyQt6 图形界面入口
├── gui/
│   ├── __init__.py
│   ├── app.py                   ← 主窗口
│   └── utils/
│       ├── __init__.py
│       ├── backup_engine.py     ← 备份引擎
│       ├── drive_detector.py    ← 目标检测
│       └── styles.py            ← 深色主题样式
├── scripts/
│   ├── memory.py                ← 核心记忆引擎（~1366行）
│   ├── scanner.py               ← 全覆盖备份引擎（~495行）
│   ├── detector.py              ← AI 工具自动发现（~299行）
│   ├── rules_engine.py          ← 规则匹配引擎（~387行）
│   ├── usb_detector.py          ← U 盘检测（~364行）
│   ├── streamlit_app.py         ← Web UI（~612行）
│   ├── auto_extract/            ← v4.2 自动提取模块
│   │   ├── __init__.py
│   │   ├── base_schema.yaml     ← 官方骨架（已知路径）
│   │   ├── user_schema.yaml     ← 用户实际路径（自动生成）
│   │   ├── schema_generator.py  ← 路径扫描引擎
│   │   ├── extract_runner.py    ← 差异对比 + 备份执行
│   │   └── backup_engine.py     ← 备份底层引擎
│   ├── task_schema/             ← Schema 任务进度表（~256行）
│   │   ├── schema_models.py     ← 数据模型（TaskSchema / FileRef）
│   │   ├── validator.py         ← 规则引擎
│   │   ├── registry.py          ← YAML 读写接口
│   │   ├── registry.yaml        ← 任务总表
│   │   └── README.md            ← Schema 子模块文档
│   └── config/
│       ├── ai_tools.yaml        ← AI 工具路径库
│       └── scan_rules.yaml      ← 扫描规则
└── assets/                      ← [init 后自动创建]
    ├── chronicle/               ← 事件流记忆
    ├── monograph/               ← 专题记忆
    └── index/                   ← 关键词索引
```

**代码量**：核心脚本 ~3523 行 + Schema ~256 行 + GUI ~829 行 = **约 4600+ 行**

---

## 怎么用

### 依赖要求

- **Python** ≥ 3.9
- **零硬性外部依赖**：核心引擎纯标准库实现
- **可选**：PyYAML（YAML 配置解析）、PyQt6（桌面 GUI）、Streamlit（Web UI）

### 安装

```bash
# 方式一：git clone（推荐）
git clone https://github.com/Gabe-luv-Nancy/hippocampus.git
cd hippocampus

# 方式二：OpenClaw Skill 一键安装
openclaw skill install hippocampus
```

### 初始化（首次必运行）

```bash
python3 scripts/memory.py init
```

初始化会创建 `assets/` 目录结构（chronicle / monograph / index）并建立 SQLite 索引。

### 验证

```bash
python3 scripts/memory.py status
# 应显示 Chronicle 和 Monograph 状态，record count 0
```

### 基本命令

```bash
# 记忆管理
python3 scripts/memory.py save "内容"     # 保存记忆
python3 scripts/memory.py recall 关键词   # 精确检索
python3 scripts/memory.py new 专题名      # 创建专题
python3 scripts/memory.py analyze         # 分析事件流，升级到专题
python3 scripts/memory.py autocheck       # 自动检查并保存

# AI 工具扫描
python3 scripts/detector.py               # 检测已安装的 AI 工具
python3 scripts/scanner.py scan           # 全量扫描
python3 scripts/scanner.py scan --tool openclaw  # 只扫指定工具
python3 scripts/scanner.py scan --usb /path     # 备份到 U 盘

# Schema 任务管理
python3 scripts/task_schema/registry.py list        # 查看任务表
python3 scripts/task_schema/registry.py get <id>    # 查看单个任务
python3 scripts/task_schema/validator.py check <id> # 校验任务状态

# Auto-Extract（v4.2）
python3 scripts/auto_extract/extract_runner.py --dry-run  # 预览
python3 scripts/auto_extract/extract_runner.py            # 执行备份
```

### 图形界面

```bash
# PyQt6 桌面应用（推荐）
python3 gui_main.py --mode local               # 本地版
python3 gui_main.py --mode disk --path "F:/"   # U 盘浏览模式

# Streamlit Web UI
streamlit run scripts/streamlit_app.py
```

### Cron 定时任务

```bash
# 每 6 小时自动保存
openclaw cron add --name "hippocampus-autosave" \
  --schedule "0 */6 * * *" --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py autocheck"

# 每天 23:00 分析事件流
openclaw cron add --name "hippocampus-analyze" \
  --schedule "0 23 * * *" --session-target isolated \
  --payload "Run: python3 /path/to/scripts/memory.py analyze"
```

### 触发关键词

在 AI 对话中使用以下词可触发记忆操作：

`remember` / `recall` / `checkpoint` / `记得` / `记忆` / `schema` / `task` / `warn`

### 用户配置

编辑 `USER_CONFIG.md`（首次 init 后可自定义），支持以下配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ROUND_THRESHOLD` | 25 | 触发自动保存的对话轮数 |
| `TIME_HOURS` | 6 | 触发自动保存的小时数 |
| `TOKEN_THRESHOLD` | 10000 | Token 阈值 |
| `AUTO_SAVE` | true | 是否自动保存 |
| `BASE_PATH` | ./assets | 记忆存储根目录 |
| `CHRONICLE_DIR` | chronicle | 事件流目录名 |
| `MONOGRAPH_DIR` | monograph | 专题目录名 |
| `INDEX_DIR` | index | 索引目录名 |
| `KEYWORD_COUNT` | 20 | 关键词提取数量 |
| `ASSOCIATION_DEPTH` | 3 | 关联深度 |
| `FILE_ORG_ENABLED` | true | 文件组织功能开关 |
| `FILE_ORG_AUTO_MOVE` | false | 自动移动文件开关 |
| `FILE_SCAN_PATHS` | ./workspace | 文件扫描路径 |
| `FILE_EXCLUDE_PATHS` | .openclaw,node_modules,.git | 排除路径 |

---

## 怎么发布

### 版本号管理

版本号文件：`VERSION`（内容为 `X.Y.Z`，遵循 [SemVer](https://semver.org/)）

**更新流程**：

1. 确定新版本号
2. 更新 `VERSION` 文件内容
3. 更新 `skill.yaml` 中 `version` 字段
4. 更新本 README 中的版本徽章（第 5 行）和版本历史
5. 同步更新 Clawhub 版和 USB 版的对应文件

### Git Tag + GitHub Release

```bash
# 1. 提交所有改动
git add -A
git commit -m "release: vX.Y.Z — 一句话描述"

# 2. 打 tag
git tag -a vX.Y.Z -m "vX.Y.Z release"

# 3. 推送代码和 tag
git push origin main
git push origin vX.Y.Z

# 4. 在 GitHub 上创建 Release（或用 gh CLI）
gh release create vX.Y.Z --title "vX.Y.Z" --notes "发布说明"
```

### 同步到其他版本

GitHub 版是**源码主库**，其他版本从这同步：

```
GitHub 版（源码）— 你在这里
    ↓ 脚本/PROMPT.md 方式同步
Clawhub 版（PROMPT.md + scripts/）
    ↓ AI 自动部署
用户机器上的 Hippocampus Skill
    ↓ scanner.py 扫描
BrainDump U 盘
```

**同步清单**：

| 同步项 | 目标版本 | 操作 |
|--------|---------|------|
| `scripts/` 目录 | Clawhub | 复制到 `hippocampus-for-clawhub/scripts/` |
| `gui_main.py` | Clawhub | 复制到 `hippocampus-for-clawhub/gui_main.py` |
| `scripts/` 核心引擎 | USB | 复制到 `hippocampus-for-usb/brain_dump_linux/lib/` |
| 版本号 | 全部 | 统一更新 VERSION / skill.yaml / README |
| CHANGELOG | 全部 | 追加版本历史记录 |

> ⚠️ USB 版的 Hippocampus.exe 必须在 **Windows 原生环境** PyInstaller 打包（WSL 打出来是 ELF）

---

## 核心模块详解

### 🔥 Schema — AI 任务进度表（v4.0 核心）

让 AI 照章办事、无法赖账的任务管理系统。

**工作流**：

```
AI: "我要把任务 HIPPO-XXX 标记为 done"
        ↓
validator.py: "你的 file_refs 全部 verified=true 了吗？"
        ↓
AI: 逐个文件路径验证 → 只有文件真实存在才能写入 done
        ↓
写不进去就是写不进去，AI 无可争辩
```

**数据模型**：

| 模型 | 字段 | 说明 |
|------|------|------|
| `TaskSchema` | `id` | 格式：`HIPPO-YYYYMMDD-NNN` |
| | `title` | 任务标题（≤100 字） |
| | `status` | `proposed` / `approved` / `in_progress` / `done` |
| | `assignee` | `ran` / `fep` / `bes` / `ed` |
| | `phase` | `v4.1` / `v4.2` / `v4.3` |
| | `file_refs` | 需验证的文件引用列表 |
| | `depends_on` | 依赖的其他任务 ID |
| `FileRef` | `path` | 文件真实路径（POSIX 格式） |
| | `verified` | `True` = 文件存在已确认 |

**验证规则**：

| 场景 | 合法？ | 原因 |
|------|--------|------|
| `status="proposed"`，无 `file_refs` | ✅ | 没有需要验证的 |
| `status="done"`，所有 `file_refs[].verified=true` | ✅ | 全部文件已确认 |
| `status="done"`，有 `file_refs[].verified=false` | ❌ | 存在未验证文件 |
| `verified=true` 但路径不存在 | ❌ | 文件未找到 |
| 任务依赖未完成 | ❌ | 上游未 done |

**文件列表**：`scripts/task_schema/` 下共 4 个核心文件（~256 行）：

- `schema_models.py` — `TaskSchema` / `FileRef` 数据类
- `validator.py` — 强制打钩规则引擎
- `registry.py` — YAML 读写接口（load / save / add / update / list / validate_all）
- `registry.yaml` — 任务总表

**Python 调用示例**：

```python
import sys
sys.path.insert(0, "scripts/task_schema")
from schema_models import TaskSchema, FileRef
from registry import load_registry, get_task, list_tasks

# 加载所有任务
tasks = load_registry("scripts/task_schema/registry.yaml")

# 按状态查询
in_progress = list_tasks("scripts/task_schema/registry.yaml", status="in_progress")
```

---

### 📦 Scanner — 全覆盖备份引擎

```
扫描主机文件 → 计算 SHA256
    ↓
对比已有记录：hash 一致 → SKIP / hash 不同 → 复制
    ↓
两端日志逐一对照（客户端 + U 盘）
```

支持 12+ 种 AI 工具：OpenClaw / Kimi / 豆包 / ChatGLM / 智谱 / 通义千问 / 文心一言 / Gemini / Claude / DeepSeek / 讯飞星火 / 元宝

**配置文件**：
- `scripts/config/scan_rules.yaml` — 扫描规则
- `scripts/config/ai_tools.yaml` — AI 工具路径库

---

### 🧠 Memory — 双层记忆引擎

- **Chronicle（事件流）**：自动保存对话记录，带精确时间戳
- **Monograph（专题）**：重要主题，丰富元数据，支持跨主题交叉引用

核心入口：`scripts/memory.py`（~1366 行），纯标准库实现。

---

### 🔍 Auto-Extract — 自动提取模块（v4.2）

自动识别用户通过 AI 新形成的记忆文件并备份到 Monograph 层。

**工作流**：

```
base_schema.yaml          ← 官方骨架（已知路径）
     ↓
schema_generator.py       ← 扫描用户实际路径 → user_schema.yaml
     ↓
extract_runner.py         ← 对比两者差异，备份新文件
     ↓
backup_engine.py          ← 同名文件加时间戳，全新文件直接复制
```

**文件列表**：`scripts/auto_extract/` 下共 5 个核心文件：

- `base_schema.yaml` — 官方路径骨架
- `user_schema.yaml` — 用户实际路径（自动生成，勿手动编辑）
- `schema_generator.py` — 路径扫描引擎
- `extract_runner.py` — 差异对比 + 备份执行
- `backup_engine.py` — 备份底层引擎

---

### 🔎 Detector — AI 工具自动发现

`scripts/detector.py`（~299 行），扫描主机检测已安装的 AI 工具，输出工具名 + 路径列表。

---

### ⚡ 其他模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 规则匹配引擎 | `scripts/rules_engine.py`（~387行） | 可配置的文件匹配规则 |
| U 盘检测 | `scripts/usb_detector.py`（~364行） | 热拔插检测 |
| PyQt6 GUI | `gui_main.py` + `gui/` | 深色主题桌面应用 |
| Streamlit Web UI | `scripts/streamlit_app.py`（~612行） | 浏览器访问的记忆管理界面 |

---

## 命令速查表

| 命令 | 说明 |
|------|------|
| `memory.py init` | 初始化数据库和目录（首次必运行） |
| `memory.py status` | 查看记忆状态 |
| `memory.py save <content>` | 保存记忆 |
| `memory.py recall <keyword>` | 精确检索 |
| `memory.py new <topic>` | 创建专题 |
| `memory.py analyze` | 分析事件流，升级到专题 |
| `memory.py autocheck` | 自动检查并保存 |
| `scanner.py scan` | 全量扫描 AI 工具 |
| `scanner.py scan --usb <path>` | 备份到 U 盘 |
| `scanner.py scan --tool <name>` | 只扫描指定工具 |
| `detector.py` | 检测已安装的 AI 工具 |
| `task_schema/registry.py list` | 查看 Schema 任务表 |
| `task_schema/registry.py get <id>` | 查看单个任务 |
| `task_schema/validator.py check <id>` | 校验任务状态 |
| `auto_extract/extract_runner.py --dry-run` | 预览自动提取 |
| `auto_extract/extract_runner.py` | 执行自动提取 |
| `gui_main.py --mode local` | 启动本地 GUI |
| `gui_main.py --mode disk --path <p>` | 启动 U 盘浏览模式 |

---

## 版本历史

### v4.2.0 (2026-04) — Auto-Extract

- `scripts/auto_extract/` 模块（base_schema / generator / runner / backup）
- 自动识别用户通过 AI 新形成的记忆文件并备份到 Monograph 层
- 同名文件加时间戳，全新文件直接复制

### v4.0.0 (2026-05) — 三版本统一 + Schema

**核心创新**：
- Schema 模块：`schema_models.py` / `validator.py` / `registry.py`（共 256 行）
- 强制打钩规则：`status=done` 必须所有 `file_refs[].verified=true`
- 路径校验：`verified=true` 要求文件真实存在于磁盘
- 依赖链路：`depends_on`，上游未 done 下游不能 done
- 三版统一至 v4.0.0
- 技术创新：YAML-based registry，无外部依赖，标准库实现

### v3.1.0 (2026-03) — GUI + 察言观色

- PyQt6 图形界面（gui_main.py + gui/app.py）
- 察言观色：高频心跳 / 即时触发 / 阈值触发 / 停用词过滤
- U 盘预建 SQLite，支持离线浏览

### v3.0.0 (2026-02) — AI 工具发现 + 全覆盖备份

- `detector.py`（299行）：自动检测主机 AI 工具
- `scanner.py`（495行）：SHA256 增量备份
- `rules_engine.py`（387行）：规则匹配引擎
- 支持 12+ 种 AI 工具

### v2.0.0 — 知识图谱 + 自动分析

- Skill → Project → Goal 网状关联
- Cron 自动分析事件流
- `usb_detector.py`（364行）：U 盘热拔插检测

### v1.0.0 — 双层记忆系统

- Chronicle + Monograph 双存储架构
- SQLite 全文索引
- `memory.py` 核心引擎（1366行）

---

## 为什么叫"海马体"？

海马体（Hippocampus）是大脑中负责记忆的核心结构。

AI 的终极形态——**永不遗忘，精确检索，主动预警**。

---

## License

MIT © GabetopZ

---

## 联系方式

- GitHub: https://github.com/Gabe-luv-Nancy/hippocampus
- Issues: https://github.com/Gabe-luv-Nancy/hippocampus/issues
