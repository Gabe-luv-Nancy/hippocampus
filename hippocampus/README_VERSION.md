# Hippocampus 版本管理方案

## 目录结构

```
workspace/hippocampus/
├── hippocampus/                    ← 发行版 (Distribution)
├── hippocampus-after-installation/ ← 安装版 (Installation)
└── README_VERSION.md              ← 本文档

workspace/skills/
└── hippocampus/                   ← 安装版副本 (实际使用)
```

---

## 版本说明

### Photon 版本 (3.0.0) - 当前版本

**核心理念**: AI 应修复人类记忆缺陷，而非模仿它们

| 特性 | 说明 |
|------|------|
| **No Decay** | AI 永不遗忘 |
| **Precise Retrieval** | 精确时间戳，而非"最近" |
| **Success Tracking** | 记住成功/失败的工具和命令 |
| **Project Checkpoints** | 精确记录项目状态 |
| **Failure Warning** | 主动警告重复错误 |

---

### 1. 发行版 (hippocampus/)

**位置**: `workspace/hippocampus/hippocampus/`

**用途**: 
- 从 GitHub 克隆的干净分发版本
- 遵循 clawhub.ai 上传要求（无非文本文件）
- 遵循 GitHub 上传要求
- **所有代码修改必须从这里开始**

**内容**:
- SKILL.md (AI 指令 - Photon 版本)
- README.md (用户文档)
- USER_CONFIG.md (用户配置)
- skill.yaml (元数据)
- scripts/memory.py (核心引擎 v2)
- assets/ (目录结构，无实际文件 - init 后生成)

**命令前缀**: `/photon` (替代旧的 `/hip`)

| 命令 | 说明 |
|------|------|
| `/photon status` | 查看状态 |
| `/photon save` | 保存上下文 |
| `/photon recall <query>` | 精确回忆 |
| `/photon checkpoint` | 保存项目状态 |
| `/photon warn` | 检查失败模式 |
| `/photon graph` | 查看知识图谱 |

---

### 2. 安装版 (hippocampus-after-installation/)

**位置**: `workspace/hippocampus/hippocampus-after-installation/`

**用途**:
- 从发行版复制
- 运行 `memory.py init` 生成实际数据库和目录
- 包含实际用户数据和生成的 SQLite 数据库
- 可用于功能验证和代码分析

**内容** (除发行版内容外):
- `assets/hippocampus/chronicle/db.sqlite` (SQLite 数据库)
- `assets/hippocampus/chronicle/*.md` (记忆文件)
- `assets/hippocampus/monograph/*.md` (专题文件)
- `assets/hippocampus/index/` (索引文件)

---

### 3. 实际使用版 (skills/hippocampus/)

**位置**: `workspace/skills/hippocampus/`

**用途**:
- OpenClaw 实际加载的 skill
- 从安装版同步
- 用于功能验证、实际代码分析
- **问题修复：需回溯到发行版修改**

---

## 版本同步规则

### 发行版 → 安装版

当发行版更新后：
```bash
# 1. 更新发行版
cd workspace/hippocampus/hippocampus
git pull origin master

# 2. 重新生成安装版（保留用户数据）
cd workspace/hippocampus
rm -rf hippocampus-after-installation
cp -r hippocampus hippocampus-after-installation
cd hippocampus-after-installation
python3 scripts/memory.py init

# 3. 同步到实际使用
rm -rf workspace/skills/hippocampus
cp -r hippocampus-after-installation workspace/skills/hippocampus
```

### 问题修复流程

1. **发现问题** → 检查 `skills/hippocampus/` 或 `hippocampus-after-installation/`
2. **定位问题** → 追溯到 `hippocampus/hippocampus/` (发行版)
3. **修改发行版** → 测试验证
4. **推送到 GitHub** → 同步更新安装版

---

## GitHub 仓库

- 仓库: https://github.com/Gabe-luv-Nancy/hippocampus
- 分支: master
- 内容: 发行版完整内容 (Photon v3.0.0)

---

## 版本历史

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-21 | Photon 3.0.0 | 新哲学：AI 修复记忆缺陷，命令改为 /photon |
| 2026-03-14 | v2.2.0 | 双存储架构完成 |

---

## 注意事项

1. **不要直接修改安装版或实际使用版** - 所有修改必须在发行版进行
2. **发行版保持干净** - 不包含用户数据、数据库等运行时生成的文件
3. **定期同步** - GitHub 推送后及时更新本地安装版
4. **备份用户数据** - 用户数据存储在 `hippocampus-after-installation/assets/hippocampus/`

---

## 快速命令

```bash
# 初始化/更新安装版（保留用户数据）
cd workspace/hippocampus
rm -rf hippocampus-after-installation
cp -r hippocampus hippocampus-after-installation
cd hippocampus-after-installation
python3 scripts/memory.py init

# 同步到实际使用
rm -rf workspace/skills/hippocampus
cp -r hippocampus-after-installation workspace/skills/hippocampus

# 推送发行版到 GitHub
cd hippocampus
git add .
git commit -m "Update description"
git push origin master
```
