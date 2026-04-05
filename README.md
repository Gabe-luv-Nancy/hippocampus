# Hippocampus - AI 记忆增强系统

> **核心理念**: AI 应修复人类记忆缺陷，而非模仿它们。
> 
> 传统记忆系统使用衰减模型 (0.99^days) — 这是**错误的**。AI **永不遗忘**。这才是重点。

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-OpenClaw-orange.svg" alt="Platform">
</p>

---

## ✨ 特性

| 特性 | 说明 |
|------|------|
| **No Decay** | AI 永不遗忘 |
| **精确检索** | 时间戳而非"最近" |
| **记忆抓取** | 自动收集各路 AI 的记忆文件 |
| **双重存储** | SQLite 索引 + Markdown 文件 |
| **知识图谱** | 关联分析与发现 |
| **失败预警** | 主动警告重复错误 |

---

## 🚀 快速开始

### 安装

#### 方式一：Clawhub（推荐）

```bash
# 在 OpenClaw 中执行
安装 hippocampus
```

#### 方式二：GitHub

```bash
# 克隆仓库
git clone https://github.com/Gabe-luv-Nancy/hippocampus.git

# 进入目录
cd hippocampus/hippocampus-for-github

# 初始化
python3 scripts/memory.py init
```

---

## 📁 项目结构

```
hippocampus/
├── hippocampus-for-github/      ← 💻 完整发行版（预构建）
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── memory.py            ← 核心引擎
│   │   ├── capture.py           ← 记忆抓取
│   │   └── analyzer.py          ← 本地分析
│   ├── capture/                  ← AI 路径配置
│   │   └── openclaw.yaml
│   ├── U/                       ← 🆕 U盘产品
│   │   ├── autorun.bat          ← Windows 自动运行
│   │   └── autorun.sh           ← macOS/Linux 自动运行
│   └── docs/
│
├── hippocampus-for-clawhub/     ← 🔮 提示词发行版
│   ├── PROMPT.md               ← 安装提示词
│   └── CLAWHUB.yaml            ← Clawhub metadata
│
└── README.md                    ← 本文件
```

---

## 🔧 命令

| 命令 | 说明 |
|------|------|
| `/photon status` | 查看状态 |
| `/photon save` | 保存上下文 |
| `/photon recall <关键词>` | 精确检索 |
| `/photon checkpoint` | 保存项目状态 |
| `/photon capture` | 抓取 AI 记忆 |
| `/photon warn` | 检查失败模式 |

---

## 💾 存储架构

### 双存储系统

```
Chronicle (时序记忆)
├── 用途: 日常交互记忆
├── 存储: assets/hippocampus/chronicle/*.md
└── 索引: SQLite (按时间)

Monograph (重要事件)
├── 用途: 重要决策、经验、知识点
├── 存储: assets/hippocampus/monograph/*.md
└── 索引: SQLite (按主题)
```

---

## 🆕 v3.2 新功能

### 记忆抓取 (Capture)

自动抓取电脑上各路 AI 工具的记忆文件：

- **OpenClaw**: `~/.openclaw/workspace/memory/*.md`
- **豆包**: `~/.doubao/memory/`
- **元宝**: `~/.yuanbao/memory/`
- **讯飞星火**: `~/.iflytek/spark/memory/`

### U 盘产品

将 `U/` 目录复制到 U 盘，插入电脑后自动运行抓取和分析。

```bash
# Windows
双击 autorun.bat

# macOS/Linux
./autorun.sh
```

---

## 📊 哲学

### 为什么 AI 记忆不该"遗忘"？

| 人类记忆 | Hippocampus |
|----------|-------------|
| 遗忘 → 衰减 | 永不遗忘 |
| 模糊 → "大概" | 精确 → 时间戳 |
| 被动 → 提醒才想起来 | 主动 → 预警模式 |
| 重要性衰减 → 忘记重要的事 | 永不丢失任何信息 |

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **GitHub**: https://github.com/Gabe-luv-Nancy/hippocampus
- **Clawhub**: https://clawhub.ai/hippocampus
- **文档**: https://github.com/Gabe-luv-Nancy/hippocampus/docs

---

<p align="center">
  <sub>Built with ❤️ by GabetopZ</sub>
</p>
