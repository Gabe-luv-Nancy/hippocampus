# Hippocampus DATUM（BrainDump U盘版）

> **v4.0.0** | 别名 DATUM | AI 记忆备份 U 盘发行版
> 作者：GabetopZ | License：MIT

---

## 核心理念

用户购买 Hippocampus 本地软件 → 安装后配置要监控的 AI 工具和路径 → 插上 HIPPOCAMPUS U 盘 → 客户端自动发现、静默增量备份 → 拔出 U 盘，记忆随身带走。

**一句话**：U 盘是 AI 记忆的物理保险箱。

---

## 功能一览

| # | 功能 | 说明 | 自版本 |
|---|------|------|--------|
| 1 | **双发行包架构** | Linux 原生 + Windows WSL 桥接，同一 U 盘跨平台使用 | v4.0 |
| 2 | **U盘身份识别** | marker.txt 独家标识，只认 Hippocampus 盘 | v4.0 |
| 3 | **SHA256 增量备份** | 只复制新增/修改文件，已备份文件自动跳过 | v3.0 |
| 4 | **两端日志对照** | 客户端 + U 盘各自记录 JSON Lines 日志，可追溯 | v4.0 |
| 5 | **AI 工具自动发现** | 扫描主机检测已安装 AI 工具（12+） | v3.0 |
| 6 | **Agent 快照备份** | 跨平台 Agent 发现 + 记忆目录快照 | v4.0 |
| 7 | **本地 GUI** | 标准库 HTTP Server + 原生 HTML/JS，无浏览器弹窗 | v4.0 |
| 8 | **SQLite 索引** | 预建数据库，支持离线浏览 | v3.1 |

---

## 目录结构

U 盘产品提供两个版本，用户根据操作系统选择。两个目录**必须同级**放在 U 盘根目录：

```
U盘根目录/
├── brain_dump_linux/                ← 🐧 Linux 原生版
│   ├── Hippocampus                  ← Linux ELF 二进制（PyInstaller 打包）
│   ├── autorun.sh                   ← 交互式启动菜单
│   ├── server.py                    ← HTTP REST API
│   ├── marker.txt                   ← 独家身份标识
│   ├── lib/
│   │   ├── scanner.py               ← 文件扫描引擎
│   │   ├── memory_scanner.py        ← AI 记忆扫描器
│   │   ├── ssh_scanner.py           ← SSH/SFTP 远程扫描
│   │   ├── detector.py              ← AI 工具检测
│   │   ├── file_hasher.py           ← SHA256 文件哈希
│   │   ├── rules_engine.py          ← 规则匹配引擎
│   │   ├── usb_detector.py          ← U盘检测
│   │   ├── agent_snapshot.py        ← Agent 发现 + 记忆快照
│   │   ├── json_log.py              ← JSON Lines 日志写入器
│   │   ├── _deprecated/             ← [归档] streamlit_app.py（旧版Web UI）
│   │   └── config/
│   │       ├── ai_tools.yaml        ← AI 工具路径配置
│   │       └── scan_rules.yaml      ← 扫描规则
│   ├── db/
│   │   ├── init_db.py               ← 数据库初始化/校验
│   │   └── brain_dump.sqlite        ← SQLite 数据库
│   ├── bin/
│   │   └── receive.sh               ← 数据接收脚本
│   ├── ui/static/                   ← Web 前端（HTML/JS/CSS）
│   │   ├── index.html
│   │   ├── app.js
│   │   └── style.css
│   ├── _archived_windows_files/     ← [归档] 旧版 Windows 批处理
│   ├── capture/                     ← [自动创建] 备份文件
│   ├── output/                      ← [自动创建] 导出文件
│   └── logs/                        ← [自动创建] 操作日志
│
└── brain_dump_windows/              ← 🪟 Windows + WSL 版
    ├── autorun.bat                  ← 主启动器（WSL 桥接）
    ├── 1-本地版.bat                  ← 一键扫描本机磁盘
    ├── 2-U盘版.bat                   ← 扫描指定 U盘
    ├── wsl_bridge.py                ← 路径桥接层（Win↔WSL 互转）
    ├── marker.txt                   ← 独家身份标识（同 Linux 版）
    ├── bin/
    │   ├── receive.bat              ← 数据接收
    │   └── validate.bat             ← 数据校验
    ├── capture/                     ← [自动创建] 备份文件
    ├── output/                      ← [自动创建] 导出文件
    └── logs/                        ← [自动创建] 操作日志
```

### 架构关系

| 目录 | 运行环境 | 说明 |
|------|---------|------|
| `brain_dump_linux/` | Linux 原生 | 扫描引擎、数据库、Web UI，全部 Python 原生运行 |
| `brain_dump_windows/` | Windows + WSL2 | .bat 启动器，通过 WSL 调用 Linux 引擎 |

```
Windows 版通过 WSL 调用 Linux 引擎：
┌──────────────────────┐
│  brain_dump_windows/  │
│  autorun.bat          │
│       │ wsl 命令       │
│       ▼               │
│  brain_dump_linux/    │
│  python3 scanner.py   │
│  python3 server.py    │
└──────────────────────┘

Linux 版直接运行：
┌──────────────────────┐
│  brain_dump_linux/    │
│  bash autorun.sh      │
│  python3 scanner.py   │
└──────────────────────┘
```

> **核心原则**：引擎代码只在 Linux 上运行一次，Windows 通过 WSL 桥接调用。Windows 版不含引擎代码。

---

## 快速使用

### Windows 用户

1. 将 U 盘插入电脑
2. **确保 WSL 已安装**：在 PowerShell 运行 `wsl --install`（需重启，仅首次）
3. 双击 `brain_dump_windows/autorun.bat`
4. 选择操作开始使用

也可以直接双击：
- `1-本地版.bat` — 一键扫描本机所有磁盘（`/mnt/c/` + `/mnt/d/`）
- `2-U盘版.bat` — 输入 U 盘盘符，扫描指定磁盘

### Linux / macOS 用户

1. 将 U 盘插入电脑
2. 运行：

```bash
# 方式一：交互式菜单（推荐）
bash brain_dump_linux/autorun.sh

# 方式二：直接扫描
python3 brain_dump_linux/lib/scanner.py scan --path ~/ --output output/

# 方式三：本地 GUI（浏览器打开 http://localhost:8080）
python3 brain_dump_linux/server.py --port 8080
```

### Windows 启动器说明

| 文件 | 用途 |
|------|------|
| `autorun.bat` | 主菜单：扫描 / Web UI / 校验 |
| `1-本地版.bat` | 一键扫描本机（`/mnt/c/` + `/mnt/d/`） |
| `2-U盘版.bat` | 输入 U 盘盘符，扫描指定磁盘 |

---

## 发布指南

### 一、Linux 原生版构建

#### 方式 A：PyInstaller 打包二进制（推荐）

在 **WSL 或 Linux 原生** 环境下执行：

```bash
cd brain_dump_linux/

# 安装 PyInstaller
pip3 install pyinstaller

# 打包（无窗口模式，CLI/Server）
pyinstaller --name Hippocampus --onefile --clean \
  --add-data "lib:lib" \
  --add-data "ui:ui" \
  --add-data "db:db" \
  autorun.sh

# 复制产物
cp dist/Hippocampus .
```

产物：`brain_dump_linux/Hippocampus`（Linux ELF 二进制）

#### 方式 B：直接运行 Python（免打包）

```bash
cd brain_dump_linux/
python3 autorun.sh      # 交互式菜单
python3 server.py       # Web UI
python3 lib/scanner.py  # 命令行扫描
```

**依赖**：Python 3.9+（必须）、PyYAML（可选，扫描配置需要）。无外部依赖，无需 pip install。

### 二、Windows WSL 版构建

Windows版**不需要编译**，`.bat` 启动器和 `wsl_bridge.py` 已就绪。

**用户端前置条件**：

1. Windows 10/11 已安装 WSL2：
   ```powershell
   wsl --install
   ```
2. WSL 内已安装 Python 3.9+：
   ```bash
   sudo apt install python3 python3-pip
   ```

只需确保目录结构正确（两个目录同级放在 U 盘根目录）。

### 三、U盘烧录完整流程

```bash
# 假设 U 盘挂载在 /media/usb/
USB=/media/usb

# 1. 复制两个版本
cp -r brain_dump_linux/  $USB/brain_dump_linux/
cp -r brain_dump_windows/ $USB/brain_dump_windows/

# 2. 验证 marker.txt
cat $USB/brain_dump_linux/marker.txt
# 应输出: HIPPOCAMPUS_BRAINDUMP_v4.0.0

cat $USB/brain_dump_windows/marker.txt
# 应输出: HIPPOCAMPUS_BRAINDUMP_v4.0.0

# 3. 确保脚本可执行
chmod +x $USB/brain_dump_linux/autorun.sh
chmod +x $USB/brain_dump_linux/bin/receive.sh
chmod +x $USB/brain_dump_linux/Hippocampus
```

### 四、验证步骤

**Linux 版验证**：

```bash
cd brain_dump_linux/
python3 lib/scanner.py --help     # 扫描器可运行
python3 db/init_db.py validate    # 数据库校验
python3 server.py --port 8080 &   # Web 服务启动
```

**Windows 版验证**：

1. 双击 `brain_dump_windows/autorun.bat`
2. 应显示 WSL 检测 → Linux 引擎检测 → 操作菜单
3. 选择 [2] 启动 Web UI → 浏览器打开 http://localhost:8080

---

## 核心机制详解

### U盘身份识别（marker.txt）

U 盘根目录 `marker.txt` 内容：

```
HIPPOCAMPUS_BRAINDUMP_v4.0.0
```

**识别三步曲**：

```
Step 1  Client 轮询所有盘符/mount
Step 2  读取根目录 marker.txt 内容
Step 3  内容 == "HIPPOCAMPUS_BRAINDUMP_v4.0.0" ？
         ├─ 是  → 确认为 HIPPOCAMPUS 盘，触发增量备份
         └─ 否  → 忽略，不是我们的盘
```

其他任何 U 盘不受影响。

### 两端日志对照

客户端和 U 盘各自独立记录 JSON Lines 日志，备份完成后客户端日志同步到 U 盘。

**日志格式**：

```json
{"ts":"2026-04-22T10:01:02","side":"client","event":"FOUND","tool":"openclaw","path":"~/.openclaw/workspace/MEMORY.md","size":3244,"hash":"sha256:abc123"}
{"ts":"2026-04-22T10:01:02","side":"client","event":"SKIP","tool":"openclaw","path":"~/.openclaw/workspace/TODO.md","reason":"hash_match"}
{"ts":"2026-04-22T10:01:04","side":"usb","event":"RECEIVED","tool":"openclaw","path":"capture/openclaw/MEMORY.md","size":3244,"hash":"sha256:abc123"}
{"ts":"2026-04-22T10:01:04","side":"usb","event":"COMPLETE","total":3}
```

**日志事件类型**：

| 事件 | 端 | 说明 |
|------|-----|------|
| FOUND | client | 发现符合规则的记忆文件 |
| SKIP | client | 文件已备份（hash 一致），跳过 |
| ERROR | client | 扫描出错（如权限不足） |
| RECEIVED | usb | U盘成功接收文件 |
| CONFLICT | usb | hash 不一致（文件被修改后覆盖） |
| COMPLETE | both | 本次备份完成，统计 |

**对照能力**：

- 客户端扫描了哪些文件 → U 盘收到了哪些文件
- `SKIP (hash_match)` → 对应 U 盘的跳过记录
- 任何差异（客户端有但 U 盘没收到）立刻可发现

### 增量判断逻辑

```
客户端扫描文件 → 计算 SHA256
    ↓
查询 U盘 SQLite：SELECT hash FROM files WHERE path = ?
    ├─ hash 完全一致 → SKIP（已在 U盘）
    └─ hash 不同或记录不存在 → 复制到 U盘
```

### 客户端配置

用户安装本地软件后，通过 Client UI 点选：

1. **选择监控的 AI 工具**（勾选）
2. **配置每个工具的监控路径**（添加/删除）
3. **设置文件过滤规则**（包含/排除 glob 模式）
4. **配置 SSH 云端**（主机/用户名/密钥/监控路径）
5. **U盘状态监控**（已连接/未连接/备份历史）

配置保存在用户本地：`~/.hippocampus/config.yaml`

**Client 安装包不包含在 U 盘中**，由用户另行下载安装：

| 平台 | 安装包格式 | 安装路径 |
|------|---------|---------|
| Windows | `.exe` / `.msi` | `C:\Program Files\Hippocampus\` |
| macOS | `.dmg` | `/Applications/Hippocampus.app` |
| Linux | `.deb` / `.AppImage` | `/opt/hippocampus/` |

### 扫描规则（scan_rules.yaml）

```yaml
tools:
  openclaw:
    name: "OpenClaw"
    paths:
      - "~/.openclaw/workspace/"
      - "~/.openclaw/memory/"
    patterns:
      - "*.md"
      - "*.json"
      - "*.yaml"
    exclude:
      - "**/__pycache__/**"
      - "**/node_modules/**"
    min_size: 0
    max_size: 52428800   # 50MB

  kimi:
    name: "Kimi"
    paths:
      - "~/Library/Application Support/Kimi/"
    patterns:
      - "*.txt"
      - "conversation*.json"
    exclude:
      - "**/cache/**"

  doubao:
    name: "豆包"
    paths:
      - "~/Library/Application Support/Doubao/"
    patterns:
      - "*.json"
```

### U盘容量要求

| 版本 | 内容 | 最低容量 | 推荐 |
|------|------|---------|------|
| 轻量版 | 代码 + SQLite | 4 GB | 8 GB |
| 标准版 | 代码 + SQLite + ChromaDB | 8 GB | 16 GB |
| 完整版 | 标准版 + Qwen2-0.5B 模型 | 16 GB | 32 GB |

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| WSL 中找不到 Linux 引擎 | 确保 `brain_dump_linux/` 和 `brain_dump_windows/` 在同一目录下 |
| PyInstaller 打包失败 | 清理后重试：`rm -rf dist build __pycache__ && pyinstaller --clean ...` |
| marker.txt 验证失败 | 检查文件内容是否恰好是 `HIPPOCAMPUS_BRAINDUMP_v4.0.0`（无多余空格/换行） |
| 权限不足 | Linux 下执行 `chmod +x brain_dump_linux/autorun.sh brain_dump_linux/bin/receive.sh brain_dump_linux/Hippocampus` |
| 数据库不存在 | 运行 `python3 db/init_db.py` 初始化 |

---

## 版本历史

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| **v4.0.0** | 2026-05 | 双发行包架构（Linux 原生 + Windows WSL 桥接）；两端日志对照机制；增量 SHA256 判断；Agent 快照备份 |
| **v3.1.0** | 2026-04 | Streamlit Web UI + 前端 UI 双前端；U盘预建 SQLite |
| **v3.0.0** | 2026-03 | AI 工具自动发现；SHA256 增量备份引擎；规则匹配引擎 |
| **v2.0.0** | 2026-03 | 双存储架构；SQLite 索引 |
| **v1.0.0** | 2026-02 | 初始版本 |

---

## License

MIT License © GabetopZ

---

*本文档与 for-github / for-clawhub 版本同步更新（v4.0.0）*
