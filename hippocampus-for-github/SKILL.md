---
name: hippocampus
version: "4.0.0"
description: "Hippocampus — AI 记忆增强系统，永不遗忘，精确检索，主动预警"
category: productivity
---

# Hippocampus Skill

> "AI is meant to FIX human memory flaws, why learn human decay?"

**核心理念**：AI 永不遗忘、精确时间戳、主动预警。传统记忆系统用衰减率（0.99^days）——这是错的。AI 从不遗忘，这才是重点。

**工作台**: `/mnt/x/CLABIN/HIPPO/hippocampus-for-github/`
**版本**: 4.0.0
**三个发行版**: GitHub (源码) / Clawhub (提示词) / BrainDump U盘 (商业)

---

## 命令参考

### 核心命令

| 命令 | 说明 |
|------|------|
| `/hippo init` | 初始化数据库和目录 |
| `/hippo status` | 查看记忆状态 |
| `/hippo save` | 保存当前上下文 |
| `/hippo recall <keyword>` | 精确回忆 |
| `/hippo checkpoint` | 保存项目状态 |
| `/hippo warn` | 检查失败模式 |
| `/hippo graph` | 查看知识图谱 |
| `/hippo scan` | 扫描主机记忆文件 |
| `/hippo detect` | 检测已安装的 AI 工具 |

### 触发关键词

`remember` / `recall` / `checkpoint` / `记得` / `记忆`

---

## 关键文件路径

```
/mnt/x/CLABIN/HIPPO/hippocampus-for-github/
├── scripts/memory.py          ← [P0] 核心引擎 (1366行)
├── scripts/scanner.py         ← 扫描引擎 (495行)
├── scripts/detector.py        ← AI 工具检测 (299行)
├── scripts/rules_engine.py    ← 规则匹配 (387行)
├── scripts/usb_detector.py    ← U 盘检测 (364行)
├── scripts/streamlit_app.py   ← Web UI (612行)
├── scripts/auto_extract/      ← v4.2 自动提取模块
├── scripts/task_schema/       ← Schema 模块
├── gui_main.py                ← PyQt6 GUI (644行)
├── gui/                       ← GUI 模块包
└── scripts/config/            ← 扫描规则 + AI工具路径库
```

---

## 版本体系

| 版本 | 部署方式 | 别名 |
|------|---------|------|
| GitHub | `git clone` + 手动运行 | Hippocampus SERVO |
| Clawhub | 提示词注入，AI 自动部署 | Hippocampus REVELARE |
| BrainDump | 直接复制到 U 盘 | Hippocampus DATUM |

---

## 创新子项目

### AnswerSheet — 可验证填表明文范式

路径: `/mnt/x/CLABIN/HIPPO/AnswerSheet/`

三个核心创新：
1. 🔥 有监督/无监督双模式验证架构（行业首创）
2. 🔥 Module 权限 + 条件化 fill-in 明文融合（行业首创）
3. 🔥 Induction 归纳式验证（表单领域首创）

详见: `/mnt/x/CLABIN/HIPPO/AnswerSheet/SKILL.md`

---

## Pitfalls

- `memory.py` 是核心入口，不要单独修改，三版本共享
- GUI 需要 PyQt6：`pip install PyQt6`
- Streamlit 需要：`pip install streamlit`
- 扫描引擎依赖 `config/scan_rules.yaml` 和 `config/ai_tools.yaml`
- USB 版的 Hippocampus.exe 必须在 **Windows 原生环境** PyInstaller 打包（WSL 打出来是 ELF）
