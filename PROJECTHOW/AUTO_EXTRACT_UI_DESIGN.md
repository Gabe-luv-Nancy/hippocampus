# HIPPO Auto-Extract 前端 UI 设计文档

> 起草：2026-04-23
> 角色：fep（FrontendPlanningEngineer）
> 状态：规划稿，待 HIPPO 组确认
> 关联功能：V4.2 Auto-Extract File Memory

---

## 一、功能概述与设计目标

**Auto-Extract File Memory 核心逻辑：**

```
官方骨架（base_schema.yaml）
      ↕ diff
用户实际路径（user_schema.yaml）
      ↓
  差异分析
  ├─ NEW：用户新增文件
  ├─ MODIFIED：用户修改了骨架已有文件
  └─ SAME：无变化（不展示）
      ↓
  用户确认备份
      ↓
  备份到 assets/hippocampus/monograph/file_memory/
  ├─ 同名文件 → 加时间戳防覆盖
  └─ 新文件 → 直接复制
```

**目标用户画像：**
- 使用 HIPPO 管理个人知识库的 Operator
- 熟悉 CLI 操作，希望快速完成备份
- 有时需要可视化审查备份历史

**核心假设：**
- CLI 是主要交互方式（P0）
- Streamlit/PyQt6 是未来扩展（P2）
- base_schema.yaml 和 user_schema.yaml 由 ED 或用户维护

---

## 二、触发方式总览

| 触发方式 | 实现优先级 | 说明 |
|---------|-----------|------|
| `/hippo extract` CLI 命令 | **P0（必须）** | 立即扫描，对比差异，确认后备份 |
| `/hippo extract --dry-run` | **P0（必须）** | 预览差异，不实际备份 |
| cron 定时任务（每日） | P1 | 自动备份，配合 `hippocampus-for-usb` 使用 |
| Streamlit Web UI | P2 | 未来可选，友好可视化 |
| PyQt6 桌面 GUI | P2 | 未来可选，批量操作 |

---

## 三、CLI 界面设计（核心 P0）

### 3.1 命令清单

| 命令 | 格式 | 说明 |
|------|------|------|
| `hippo extract` | `hippo extract [--dry-run]` | 扫描差异并预览 |
| `hippo extract --confirm` | `hippo extract --confirm` | 直接执行备份（跳过确认） |
| `hippo extract --config` | `hippo extract --config=<path>` | 指定 schema 路径 |
| `hippo backup list` | `hippo backup list [--limit=<n>]` | 查看备份历史 |
| `hippo backup restore` | `hippo backup restore <file>` | 从备份恢复 |

### 3.2 执行流程

```
用户执行：hippo extract
          ↓
   加载 base_schema.yaml
   加载 user_schema.yaml
          ↓
   diff 差异分析
   ├─ NEW files
   ├─ MODIFIED files
   └─ SAME（跳过）
          ↓
   渲染差异表格
          ↓
   用户确认（Y/n）
   ├─ Y → 执行备份
   └─ n → 取消
          ↓
   备份结果报告
```

---

### 3.3 ASCII Mockups（8个核心界面）

#### 界面 1：帮助信息（`hippo extract --help`）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                    V4.2                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  用法：                                                                       ║
║    hippo extract [选项]                                                       ║
║                                                                              ║
║  选项：                                                                       ║
║    --dry-run           预览差异，不执行备份                                   ║
║    --confirm           跳过确认，直接执行备份                                  ║
║    --config <path>     指定 schema 配置目录（默认：项目根目录）                ║
║    --base <path>       指定 base_schema.yaml 路径                            ║
║    --user <path>       指定 user_schema.yaml 路径                            ║
║    --output <path>     指定备份输出目录                                       ║
║                                                                              ║
║  子命令：                                                                     ║
║    hippo backup list         查看备份历史                                     ║
║    hippo backup restore      从备份恢复（开发中）                             ║
║                                                                              ║
║  示例：                                                                       ║
║    hippo extract                    # 扫描并预览差异                          ║
║    hippo extract --dry-run          # 仅预览，不备份                           ║
║    hippo extract --confirm          # 直接备份，不询问                         ║
║    hippo backup list --limit=10      # 查看最近10条备份记录                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

#### 界面 2：Dry-Run 预览（`hippo extract --dry-run`）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory              [DRY-RUN 模式]               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📂 Schema 配置                                                               ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │ base_schema: /mnt/x/CLABIN/HIPPO/hippocampus-for-github/base_schema.yaml║
║  │ user_schema: /mnt/x/CLABIN/HIPPO/hippocampus-for-usb/user_schema.yaml ║   ║
║  │ output_dir: assets/hippocampus/monograph/file_memory/                │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  📊 差异分析结果                                            共 5 项差异      ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │ 状态   │ 类型      │ 文件路径                                        │   ║
║  ├────────┼───────────┼────────────────────────────────────────────────┤   ║
║  │  🟢NEW │ 新增文件  │ /mnt/x/.../my_notes/daily/20260423.md           │   ║
║  │  🟢NEW │ 新增文件  │ /mnt/x/.../my_notes/tags/ai.yaml                │   ║
║  │  🟡MOD │ 已修改    │ /mnt/x/.../workspace/SCHEMA_UI_DESIGN.md         │   ║
║  │  🟡MOD │ 已修改    │ /mnt/x/.../workspace/AUTO_EXTRACT_UI_DESIGN.md  │   ║
║  │  🔴SAME│ 无变化   │ /mnt/x/.../workspace/README.md                    │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  💾 预计备份操作                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │ 将复制 2 个新文件到 assets/hippocampus/monograph/file_memory/       │   ║
║  │ 将覆盖 2 个已有文件（自动加时间戳备份原文件）                          │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  ⚠ 这是预览模式，不会执行任何备份操作                                         ║
║                                                                              ║
║  继续？ [Y/n]:                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**说明：**
- 🟢 NEW = 用户新增的文件（骨架中不存在）
- 🟡 MOD = 用户修改了骨架已有的文件
- 🔴 SAME = 完全一致，不展示
- 显示预计备份操作，让用户心里有数

---

#### 界面 3：确认执行（用户输入 Y）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                    [执行中...]           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ✅ 开始备份...                                                             ⏳  ║
║                                                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │                                                                       │   ║
║  │  📄 复制: my_notes/daily/20260423.md                                 │   ║
║  │       → assets/hippocampus/monograph/file_memory/20260423.md       │   ║
║  │                                                                 ✓      │   ║
║  │                                                                       │   ║
║  │  📄 复制: my_notes/tags/ai.yaml                                      │   ║
║  │       → assets/hippocampus/monograph/file_memory/ai.yaml           │   ║
║  │                                                                 ✓      │   ║
║  │                                                                       │   ║
║  │  📄 覆盖: workspace/SCHEMA_UI_DESIGN.md                              │   ║
║  │       原文件 → assets/.../SCHEMA_UI_DESIGN.md.20260423_103045.bak   │   ║
║  │       新文件 → assets/.../SCHEMA_UI_DESIGN.md                       │   ║
║  │                                                                 ✓      │   ║
║  │                                                                       │   ║
║  │  📄 覆盖: workspace/AUTO_EXTRACT_UI_DESIGN.md                        │   ║
║  │       原文件 → assets/.../AUTO_EXTRACT_UI_DESIGN.md.20260423_103045.bak│ ║
║  │       新文件 → assets/.../AUTO_EXTRACT_UI_DESIGN.md                  │   ║
║  │                                                                 ✓      │   ║
║  │                                                                       │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  ════════════════════════════════════════════════════════════════════════    ║
║                                                                              ║
║  ✅ 备份完成！                                                               ║
║                                                                              ║
║  📊 备份统计：                                                               ║
║     新增文件：2 个                                                           ║
║     修改文件：2 个（原文件已备份为 .bak）                                    ║
║     总计：4 个文件                                                           ║
║                                                                              ║
║  📁 备份目录：assets/hippocampus/monograph/file_memory/                     ║
║  🕐 备份时间：2026-04-23 10:30:45                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**说明：**
- 每个文件操作后打勾
- 覆盖文件时保留原文件为 `.bak.时间戳` 格式
- 最后给出统计摘要

---

#### 界面 4：用户取消（用户输入 n）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ❌ 已取消备份操作                                                            ║
║                                                                              ║
║  没有文件被修改或复制。                                                       ║
║                                                                              ║
║  如需重新预览，请运行：                                                       ║
║    hippo extract --dry-run                                                  ║
║                                                                              ║
╚═══════════════════════════════════════════════════════  [耗时 0.3s] ════════╝
```

---

#### 界面 5：无差异情况

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                    [扫描完成]             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ✅ 未发现任何差异                                                            ║
║                                                                              ║
║  您的 user_schema.yaml 与 base_schema.yaml 完全一致，                        ║
║  没有需要备份的新文件或修改。                                                  ║
║                                                                              ║
║  📂 Schema 配置                                                               ║
║     base: /mnt/x/CLABIN/HIPPO/.../base_schema.yaml                           ║
║     user: /mnt/x/CLABIN/HIPPO/.../user_schema.yaml                           ║
║                                                                              ║
║  💡 提示：                                                                    ║
║     如果您刚刚新增了文件，可以稍后再运行：hippo extract --dry-run             ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════ [0.2s] ══╝
```

---

#### 界面 6：备份历史（`hippo backup list`）

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory              [备份历史]                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📁 备份目录：assets/hippocampus/monograph/file_memory/                      ║
║                                                                              ║
║  📋 备份记录                                          共 5 条（最新在前）    ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │ 时间                │ 操作类型 │ 文件数 │ 状态  │ 详情               │   ║
║  ├─────────────────────┼──────────┼────────┼───────┼────────────────────┤   ║
║  │ 2026-04-23 10:30:45 │ FULL     │ 4      │ ✅完成│ [查看]             │   ║
║  │ 2026-04-22 18:15:22 │ FULL     │ 2      │ ✅完成│ [查看]             │   ║
║  │ 2026-04-21 09:00:11 │ FULL     │ 6      │ ✅完成│ [查看]             │   ║
║  │ 2026-04-20 14:22:33 │ FULL     │ 1      │ ✅完成│ [查看]             │   ║
║  │ 2026-04-19 16:45:00 │ FULL     │ 3      │ ✅完成│ [查看]             │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║  [◀ 上一页]  第 1/1 页                                           [下一页 ▶] ║
║                                                                              ║
║  💡 提示：备份记录存储在 .backup_history.yaml 文件中                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**说明：**
- 记录每次备份的时间、操作类型、文件数
- 支持翻页查看历史

---

#### 界面 7：错误处理 - Schema 文件不存在

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                    [错误]                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ❌ 错误：Schema 配置文件不存在                                                ║
║                                                                              ║
║  找不到以下文件：                                                             ║
║                                                                              ║
║    ❌ /mnt/x/CLABIN/HIPPO/.../base_schema.yaml   （不存在）                   ║
║    ✅ /mnt/x/CLABIN/HIPPO/.../user_schema.yaml   （存在）                     ║
║                                                                              ║
║  解决方案：                                                                   ║
║    1. 确保 base_schema.yaml 存在于指定目录                                    ║
║    2. 使用 --base <path> 指定正确的 base_schema 路径                           ║
║    3. 使用 --config <path> 同时指定配置目录                                    ║
║                                                                              ║
║  提示：运行 hippo extract --help 查看所有选项                                 ║
║                                                                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

#### 界面 8：错误处理 - 备份目录无写入权限

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦴 HIPPO Auto-Extract File Memory                    [错误]                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ❌ 错误：无法写入备份目录                                                     ║
║                                                                              ║
║  路径：assets/hippocampus/monograph/file_memory/                            ║
║  原因：Permission denied（权限不足）                                         ║
║                                                                              ║
║  解决方案：                                                                   ║
║    1. 检查目录权限：ls -la assets/hippocampus/monograph/                     ║
║    2. 修改目录权限：chmod 755 assets/hippocampus/monograph/                   ║
║    3. 或使用 sudo 运行（谨慎）                                                ║
║    4. 或使用 --output <path> 指定其他可写目录                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 四、Streamlit Web UI 设计（P2，可选扩展）

**路径：** `scripts/auto_extract/streamlit_auto_extract.py`

### 4.1 三个面板设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🦴 HIPPO Auto-Extract File Memory                    V4.2   [🏠 首页] [⚙] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                         │
│  │ 📊 扫描结果   │ │ 🔍 差异预览   │ │ 📋 备份历史   │                         │
│  │    (当前)    │ │             │ │             │                         │
│  └─────────────┘ └─────────────┘ └─────────────┘                         │
│                                                                             │
│  ── 扫描配置 ────────────────────────────────────────────────────────────  │
│                                                                             │
│  base_schema路径: [________________________] [浏览...]                      │
│  user_schema路径: [________________________] [浏览...]                      │
│  备份输出目录:   [________________________] [浏览...]                      │
│                                                                             │
│  [🔄 扫描差异]                                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 状态指示器说明

| 状态 | 含义 | 显示样式 |
|------|------|---------|
| `official only` | 骨架标准文件，无用户修改 | 🟦 蓝色标签 |
| `modified` | 用户修改了骨架已有文件 | 🟡 黄色标签 |
| `new file` | 用户新增的不在骨架中的文件 | 🟢 绿色标签 |

### 4.3 Streamlit 详细布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🦴 HIPPO Auto-Extract                    [扫描结果] [差异预览] [备份历史]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  侧边栏配置：                                                                 │
│  ┌──────────────────────┐                                                    │
│  │ 🔧 扫描配置           │                                                    │
│  │ ─────────────────── │                                                    │
│  │ base_schema:        │                                                    │
│  │ [________________]  │                                                    │
│  │                      │                                                    │
│  │ user_schema:        │                                                    │
│  │ [________________]  │                                                    │
│  │                      │                                                    │
│  │ output_dir:         │                                                    │
│  │ [________________]  │                                                    │
│  │                      │                                                    │
│  │ [🔄 开始扫描]        │                                                    │
│  └──────────────────────┘                                                    │
│                                                                             │
│  主内容区：                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   ║
│  │  📊 扫描结果                                                            │   ║
│  │                                                                       │   ║
│  │  ┌────────────────────────────────────────────────────────────────┐   │   ║
│  │  │ 状态     │ 文件路径                      │ 大小   │ 操作        │   │   ║
│  │  ├──────────┼───────────────────────────────┼────────┼─────────────┤   │   ║
│  │  │ 🟢 new   │ my_notes/daily/20260423.md    │ 2.3 KB │ [☐ 备份]    │   │   ║
│  │  │ 🟢 new   │ my_notes/tags/ai.yaml         │ 0.5 KB │ [☐ 备份]    │   │   ║
│  │  │ 🟡 mod   │ workspace/SCHEMA_UI_DESIGN.md│ 12 KB  │ [☐ 备份]    │   │   ║
│  │  │ 🟡 mod   │ workspace/AUTO_EXTRACT...    │ 8 KB   │ [☐ 备份]    │   │   ║
│  │  │ 🟦 same  │ workspace/README.md           │ 1 KB   │ [—]        │   │   ║
│  │  └────────────────────────────────────────────────────────────────┘   │   ║
│  │                                                                       │   ║
│  │  已选择：4 个文件    [💾 批量备份]  [🔄 全选]  [☐ 取消全选]           │   ║
│  └──────────────────────────────────────────────────────────────────────┘   ║
│                                                                             │
│  ── 备份历史 ────────────────────────────────────────────────────────────  │
│                                                                             │
│  📋 最近备份记录：                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   ║
│  │ 2026-04-23 10:30:45 | FULL | 4 files | ✅ 完成 | [查看详情]         │   ║
│  │ 2026-04-22 18:15:22 | FULL | 2 files | ✅ 完成 | [查看详情]         │   ║
│  └──────────────────────────────────────────────────────────────────────┘   ║
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 五、PyQt6 桌面 GUI 设计（P2，可选扩展）

**路径：** `gui/auto_extract_dialog.py`

### 5.1 三个标签页设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🦴 HIPPO Auto-Extract File Memory                            [X] 关闭      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────┬────────────────┬────────────────┐                       │
│  │  📋 扫描配置    │  📊 差异列表    │  📜 备份日志    │                       │
│  └────────────────┴────────────────┴────────────────┘                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  标签页 1：扫描配置                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   ║
│  │                                                                       │   ║
│  │  Base Schema 路径：  [________________________] [浏览...]           │   ║
│  │                                                                       │   ║
│  │  User Schema 路径：  [________________________] [浏览...]           │   ║
│  │                                                                       │   ║
│  │  备份输出目录：     [________________________] [浏览...]           │   ║
│  │                                                                       │   ║
│  │  [ ] 自动备份模式（每日定时）                                          │   ║
│  │      定时时间： [09:00 ▼]                                             │   ║
│  │                                                                       │   ║
│  │                        [🔄 开始扫描]                                  │   ║
│  │                                                                       │   ║
│  └──────────────────────────────────────────────────────────────────────┘   ║
│                                                                             │
│  标签页 2：差异列表（批量选择备份）                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   ║
│  │  ☐  │ 状态 │ 文件路径                           │ 大小   │ 差异说明   │   ║
│  │─────┼──────┼────────────────────────────────────┼────────┼────────────│   ║
│  │  ☐  │ 🟢NEW│ my_notes/daily/20260423.md         │ 2.3 KB │ —        │   ║
│  │  ☐  │ 🟢NEW│ my_notes/tags/ai.yaml              │ 0.5 KB │ —        │   ║
│  │  ☐  │ 🟡MOD│ workspace/SCHEMA_UI_DESIGN.md       │ 12 KB  │ 修改时间  │   ║
│  │  ☐  │ 🟡MOD│ workspace/AUTO_EXTRACT_UI_DESIGN.. │ 8 KB   │ 修改时间  │   ║
│  │  ☑  │ 全部 │                                    │        │ [全选]    │   ║
│  └──────────────────────────────────────────────────────────────────────┘   ║
│                                                                             │
│  [💾 备份选中文件 (4)]  [🔄 刷新]                                            │
│                                                                             │
│  标签页 3：备份日志                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   ║
│  │  2026-04-23 10:30:45  ✅ 备份完成                                      │   ║
│  │     - 复制: my_notes/daily/20260423.md → assets/.../20260423.md     │   ║
│  │     - 复制: my_notes/tags/ai.yaml → assets/.../ai.yaml              │   ║
│  │     - 覆盖: workspace/SCHEMA_UI_DESIGN.md                            │   ║
│  │       (原文件备份为 .../.bak.20260423_103045)                         │   ║
│  │                                                                       │   ║
│  │  2026-04-22 18:15:22  ✅ 备份完成                                      │   ║
│  │     - 复制: ... (2 files)                                            │   ║
│  │                                                                       │   ║
│  └──────────────────────────────────────────────────────────────────────┘   ║
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 六、技术实现笔记（For bes）

### 6.1 核心文件结构

```
hippocampus-for-github/
├── scripts/
│   ├── auto_extract/
│   │   ├── __init__.py
│   │   ├── diff_engine.py        # 差异分析引擎
│   │   ├── backup_manager.py     # 备份逻辑（复制+时间戳）
│   │   ├── schema_loader.py      # YAML 加载器
│   │   └── cli.py                # CLI 命令入口
│   ├── streamlit/
│   │   └── auto_extract_app.py   # P2 Streamlit UI
│   └── ...
├── gui/
│   └── auto_extract_dialog.py    # P2 PyQt6 UI
├── assets/
│   └── hippocampus/
│       └── monograph/
│           └── file_memory/      # 备份目标目录
│               ├── .backup_history.yaml  # 备份历史记录
│               ├── SCHEMA_UI_DESIGN.md
│               └── SCHEMA_UI_DESIGN.md.20260423_103045.bak
└── ...
```

### 6.2 CLI 命令解析（建议用 argparse）

```python
# scripts/auto_extract/cli.py

import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='hippo extract',
        description='HIPPO Auto-Extract File Memory - V4.2'
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # hippo extract
    extract_parser = subparsers.add_parser('extract', help='扫描并备份差异文件')
    extract_parser.add_argument('--dry-run', action='store_true', help='仅预览，不备份')
    extract_parser.add_argument('--confirm', action='store_true', help='跳过确认，直接备份')
    extract_parser.add_argument('--config', default='.', help='schema 配置目录')
    extract_parser.add_argument('--base', help='base_schema.yaml 路径')
    extract_parser.add_argument('--user', help='user_schema.yaml 路径')
    extract_parser.add_argument('--output', help='备份输出目录')
    
    # hippo backup list
    list_parser = subparsers.add_parser('backup', help='备份管理')
    list_parser.add_argument('action', nargs='?', default='list')
    list_parser.add_argument('--limit', type=int, default=20)
    
    args = parser.parse_args()
    # 分发到对应模块
```

### 6.3 备份历史记录格式

```yaml
# assets/hippocampus/monograph/file_memory/.backup_history.yaml

backups:
  - timestamp: "2026-04-23T10:30:45+08:00"
    operation: "FULL"
    files_count: 4
    status: "success"
    details:
      - action: "copy"
        source: "my_notes/daily/20260423.md"
        destination: "file_memory/20260423.md"
      - action: "copy"
        source: "my_notes/tags/ai.yaml"
        destination: "file_memory/ai.yaml"
      - action: "overwrite"
        source: "workspace/SCHEMA_UI_DESIGN.md"
        destination: "file_memory/SCHEMA_UI_DESIGN.md"
        backup_file: "file_memory/SCHEMA_UI_DESIGN.md.20260423_103045.bak"
      - action: "overwrite"
        source: "workspace/AUTO_EXTRACT_UI_DESIGN.md"
        destination: "file_memory/AUTO_EXTRACT_UI_DESIGN.md"
        backup_file: "file_memory/AUTO_EXTRACT_UI_DESIGN.md.20260423_103045.bak"

  - timestamp: "2026-04-22T18:15:22+08:00"
    operation: "FULL"
    files_count: 2
    status: "success"
    details: [...]
```

### 6.4 自然语言指令格式（写入 SKILL.md）

```markdown
## Auto-Extract 操作指令格式

### 扫描差异并预览
指令模式：扫描差异 / 查看有哪些新文件 / hippo extract --dry-run
示例：
  "扫描一下我和骨架之间有什么差异"
  "hippo extract --dry-run"

### 执行备份
指令模式：备份差异 / 确认备份 / hippo extract --confirm
示例：
  "把新增和修改的文件都备份一下"
  "hippo extract --confirm"

### 查看备份历史
指令模式：查看备份历史 / 最近备份记录
示例：
  "我之前备份过几次？最近一次是什么时候？"
  "hippo backup list --limit=10"
```

---

## 七、交互状态机

```
                    ┌─────────────────┐
                    │   IDLE          │
                    │   初始状态       │
                    └────────┬────────┘
                             │ hippo extract
                             ▼
                    ┌─────────────────┐
                    │   LOADING       │
                    │   加载 Schema    │
                    └────────┬────────┘
                             │ 成功/失败
                             ▼
              ┌──────────────┴──────────────┐
              │                              │
              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │   NO_DIFF       │            │   DIFF_FOUND    │
    │   无差异        │            │   有差异待处理   │
    └────────┬────────┘            └────────┬────────┘
             │                              │
             │                              ▼
             │                    ┌─────────────────┐
             │                    │   DRY_RUN /     │
             │                    │   CONFIRM_ASK   │
             │                    │   预览/确认      │
             │                    └────────┬────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐            ┌─────────────────┐
    │   BACKUP_LIST   │◄───────────│ user input Y/n  │
    │   展示备份历史   │            │                 │
    └────────┬────────┘            └────────┬────────┘
             │                              │
             │                              │ Y
             │                              ▼
             │                    ┌─────────────────┐
             │                    │   BACKUP_EXEC   │
             │                    │   执行备份      │
             │                    └────────┬────────┘
             │                              │
             │                              ▼
             │                    ┌─────────────────┐
             │                    │   COMPLETE      │
             │                    │   备份完成      │
             │                    └─────────────────┘
             │
             │ n
             ▼
    ┌─────────────────┐
    │   CANCELLED     │
    │   已取消        │
    └─────────────────┘
```

---

## 八、Cron 定时任务配置（P1）

### 8.1 crontab 示例

```bash
# 每天早上 9:00 自动备份
0 9 * * * cd /mnt/x/CLABIN/HIPPO/hippocampus-for-github && python -m scripts.auto_extract.cli extract --confirm >> /var/log/hippo_backup.log 2>&1

# 每周日凌晨 2:00 清理 30 天前的 .bak 文件
0 2 * * 0 find /mnt/x/CLABIN/HIPPO/assets/hippocampus/monograph/file_memory/ -name "*.bak" -mtime +30 -delete
```

### 8.2 自动备份模式说明

| 设置项 | 说明 |
|-------|------|
| `--auto` | 启用自动备份模式 |
| `--schedule` | 指定 cron 表达式（替代 crontab 手动配置） |
| `--quiet` | 自动备份时静默执行，不交互 |
| `--log` | 指定日志文件路径 |

---

*本文档由 fep 起草，用于 Auto-Extract File Memory 前端 UI 规划。供 HIPPO 组 bes/fep/ran 参考，ED 审批后生效。*
