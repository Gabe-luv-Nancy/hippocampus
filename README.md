# Hippocampus

> **v4.0.0** | "AI is meant to FIX human memory flaws, why learn human decay?"

**核心理念**：AI 永不遗忘、精确时间戳、主动预警。传统记忆系统用衰减率（0.99^days）——这是错的。AI 从不遗忘，这才是重点。

大众极客化，永远追不上 Github 上最快那一批，只能不断优化产品化，U 盘极简化。

---

## 项目结构

```
HIPPO/
│
├── README.md                         ← 你在这里（总入口）
│
├── hippocampus-for-github/           ← GitHub 发行版（源码）— 详见其 README.md
│   └── README.md                     ← ✅ 全覆盖文档（安装/使用/发布/模块详解/版本历史）
│
├── hippocampus-for-clawhub/          ← Clawhub 发行版（提示词注入）— 详见其 README.md
│   └── README.md                     ← ✅ 全覆盖文档（安装/使用/发布/部署流程/AI集成）
│
├── hippocampus-for-usb/              ← BrainDump U盘产品（商业交付）— 详见其 README.md
│   └── README.md                     ← ✅ 全覆盖文档（使用/构建/烧录/核心机制/FAQ）
│
├── AnswerSheet/                      ← 【创新子项目】可验证填表明文范式
│   └── README.md                     ← 子项目独立文档
│
├── PROJECTHOW/                       ← 规划文档
└── HIPPOHOW/                         ← 管理文档
```

---

## 三个版本一览

| 版本 | 别名 | 部署方式 | 交付物 | 文档入口 |
|------|------|---------|--------|---------|
| **GitHub** | SERVO | `git clone` + 手动运行 | 完整源码 | [`hippocampus-for-github/README.md`](hippocampus-for-github/README.md) |
| **Clawhub** | REVELARE | 提示词注入，AI 自动部署 | `PROMPT.md`（纯提示词） | [`hippocampus-for-clawhub/README.md`](hippocampus-for-clawhub/README.md) |
| **BrainDump** | DATUM | 直接复制到 U 盘 | 文件夹 + 预建数据库 | [`hippocampus-for-usb/README.md`](hippocampus-for-usb/README.md) |

**每个版本的 README 都是一份全覆盖文档**，包含：核心理念、功能说明、目录结构、怎么用、怎么发布、模块详解、版本历史。

### 版本交互关系

```
GitHub 版本（源码）
    ↓
Clawhub 版本（PROMPT.md）
    ↓ AI 自动部署
用户电脑上的 Hippocampus Skill
    ↓ scanner.py 扫描主机 .md 文件
    ↓ 检测到 BrainDump U 盘插入
    ↓ 写入 db/brain_dump.sqlite + copy 原始文件
BrainDump U 盘（随身携带）
```

---

## 核心创新

### 🔥 AnswerSheet — 可验证填表明文范式

**路径**: `AnswerSheet/`

一种纯明文的可验证填表格式，以 `.md` 文件为载体。三个核心创新：

1. **有监督/无监督双模式验证架构** — 创建者预存哈希（有监督）或通过归纳规则（无监督）验证填写内容
2. **Module 权限 + 条件化 fill-in 明文融合** — 角色权限声明直接嵌入 Markdown slot 语法
3. **Induction 归纳式验证引擎** — 从多份已验证实例中自动归纳出规则

技术栈：纯 Python + PyYAML，零依赖。详见 `AnswerSheet/README.md`。

---

## 哲学对比

| 人类记忆 | Hippocampus |
|---------|-------------|
| 遗忘 → | 永不遗忘 |
| 模糊匹配 → | 精确时间戳 |
| 被动触发 → | 主动预警 |
| 重要性衰减 → | 永久保留 |

---

## 快速链接

- **GitHub 仓库**：https://github.com/Gabe-luv-Nancy/hippocampus
- **GitHub 版文档**：[`hippocampus-for-github/README.md`](hippocampus-for-github/README.md)
- **Clawhub 版文档**：[`hippocampus-for-clawhub/README.md`](hippocampus-for-clawhub/README.md)
- **USB 版文档**：[`hippocampus-for-usb/README.md`](hippocampus-for-usb/README.md)
- **AnswerSheet 子项目**：[`AnswerSheet/README.md`](AnswerSheet/README.md)

---

*Version 4.0.0 | Created by [Gabe](https://github.com/Gabe-luv-Nancy) | Engine by 赫墨 (Hermes Agent)*
