# 记忆系统状态

## 最后更新: 2026-03-21 09:07

### 系统状态

- **MemOS**: ✅ 正常运行 (1个插件已加载, 0个错误)
- **数据库**: ✅ 存在 (~6.6MB, 最后更新: 2026-03-19 19:39)
- **传统记忆文件**: ✅ 31个 .md 文件

### Cron 任务状态 (2026-03-21)

| 任务 | 状态 | 备注 |
|------|------|------|
| memory-backup-evening | ⚠️ ERROR | LLM超时问题（连续2次）|
| memory-backup-check | ✅ OK | 每日00:00检查 |
| memory-check-double | ✅ OK | 每日07:00检查 |
| hippocampus-photon-autosave | ⚠️ ERROR | Channel配置缺失（连续8次）|
| hippocampus-photon-daily | ⚠️ ERROR | 1次连续错误 |
| skill-upgrade-check | ✅ OK | 正常 |

### 已知问题

1. **memory-backup-evening LLM超时**
   - 连续2次失败，需检查 LLM 连接配置
2. **hippocampus-photon-autosave Channel配置**
   - 连续8次错误，需配置 delivery.channel

---

## 用户偏好与工作习惯

### 报告撰写偏好
- 高管团队：每人需要单独详细履历
- 区域市场：分国家详细分析
- 风险章节：删除
- 结论：只留概括，正文需详细数据

### 代码生成
- 禁止使用 GLM-5（智谱 API 不稳定）
- 所有代码生成必须通过 Cline 执行
- Cline CLI 路径：`C:\Users\GabetopZ\AppData\Roaming\npmcline.cmd`

### 工作目录
- LOTT 项目：`X:\LOTT`

---

## 重要项目

### LOTT 量化系统
- **项目路径**: `X:\LOTT`
- **数据库**: TimescaleDB (localhost:5432, lott, admin/admin123)
- **模块**:
  - timescale_config.py - 配置
  - timescale_connection.py - 连接管理
  - timescale_tables.py - 表结构
  - json_importer.py - JSON导入
  - timescale_examples.py - 示例

### 数据采集
- SHFE: AkShare 可用，数据到2026-02-13
- DCE: 有瑞数反爬，浏览器模拟也困难
- CZCE/CFFEX: 需要其他数据源

---

## 重要笔记

### Cline 子任务调用流程
**文件**: `CLINE_SUBTASK_GUIDE.md`

当需要通过 Cline 执行代码生成任务时，必须：
1. **调用方式**: 通过 `cline_runner.py` → PowerShell → Windows Python
2. **核心命令**: 
   ```
   /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "python ..."
   ```
3. **任务模板**: 参考 `CLINE_SUBTASK_GUIDE.md` 中的模板构建任务
4. **验证**: 任务完成后必须通过 Windows Python 验证执行结果

### 记忆备份 Cron 任务配置
- **双重保障机制**:
  | 时间 | 任务 |
  |------|------|
  | 23:00 | memory-backup-evening - 记忆备份 |
  | 00:00 | memory-backup-check - 检查昨天备份 |
  | 07:00 | memory-check-double - 双重检查 |

### API配置
- Minimax 正确模型：`MiniMax-M2.5-highspeed`
- 端点：`https://api.minimaxi.com/v1`

### Git/备份
- GitHub push 有时超时（443端口不稳定）
- 本地领先时需要 rebase 后再 push

---

## 📌 四大任务主线

### 主线1：LOTT 量化系统工程（X:\LOTT）
- 数据库集成（TimescaleDB）
- 数据采集（AkShare/CTP）
- 策略开发

### 主线2：Hippocampus 技能开发
- 主动记忆系统
- 自动保存机制

### 支线1：公文撰写与特定信息获取
- 报告生成
- 信息检索

### 支线2：发散性任务与信息获取
- 浏览器自动化
- 数据分析

---

## 记忆文件列表

- 2026-02-27.md
- 2026-03-05.md
- 2026-03-10.md
- 2026-03-11.md
- 2026-03-12.md
- 2026-03-13.md
- 2026-03-15.md
- 2026-03-16.md
- 2026-03-17.md
- 2026-03-20.md ← 补做备份
- 2026-03-21.md ← 今日备份
- CORE_AI_INTEGRATION.md
- CLINE_SUBTASK_GUIDE.md ← 重要！Cline调用全流程
- IMPORTED_CONFIG.md
- LOTT_CLINE_INTEGRATION.md
- LOTT_CLINE_TEMPLATES.md
- LOTT_DEVELOPMENT.md
- LOTT_QUICKREF.md
- MEMORY.md
- MINIMAX_CONFIG.md
- SECURITY.md
- requirements-simnow.md
- 量化交易技术方案-CTP与数据源.md
- 工作规范.md

---

## 历史记录

### 2026-03-21 日常工作
- **记忆备份检查**: 发现3月20日未备份，立即补做
- **补做记录**: 创建 2026-03-20.md 文件

### 2026-03-20 日常工作 ⚠️ 补做
- **cron 记忆备份任务**: 执行每日记忆备份
- **MEMORY.md 更新**: 更新 Cron 任务状态
- **创建记忆文件**: 2026-03-21.md

### 2026-03-20 日常工作
- **Heartbeat 系统检查**: 执行第6次 heartbeat 检查
- **MemOS 状态**: 1个插件已加载，0错误 ✅
- **数据库状态**: 6.6MB，最后更新 2026-03-19 19:39 ✅
- **传统记忆文件**: 30个 .md 文件 ✅
- **Git 提交**: 补做记忆备份 2026-03-19

### 2026-03-19 日常工作
- **Heartbeat 系统检查**: 执行双重记忆系统心跳检测
- **MemOS 状态**: 1个插件已加载，0错误 ✅
- **数据库状态**: 6.2MB，最后更新 2026-03-18 23:28 ✅
- **传统记忆文件**: 29个 .md 文件

### 2026-03-18 日常工作
- **Heartbeat 检查**: 执行系统巡检，确认 MemOS、数据库、记忆文件状态正常
- **Git 仓库**: master 分支领先 origin/master 3个提交

### 2026-03-17 日常工作
- **工作规范更新**: 更新四大任务主线
- **Cline 调用规范**: 强调 GLM-5 仅供 Cline 使用

### 2026-03-15 日常工作
- **WSL 代理配置**: 配置 mirrored 模式
- **Clash Verge 端口更新**: 代理端口改为 **7897**
- **技能启用**: 28个技能全部激活

### 2026-03-12 日常工作
- **ClawdHub CLI 安装**: 成功安装 v0.3.0
- **Skills 大规模安装**: 安装21个 skills

### 2026-03-11 日常工作
- **LOTT TimescaleDB 集成**: 创建6个配置文件
- **Cline 集成配置**: 配置 Windows Cline 调用

### 火山引擎研究报告 (2026-03-10)
- 字节跳动高管团队：梁汝波、周受资、张楠、陈熙、刘思齐、朱骏
- 火山引擎管理团队：谭待、张鑫、陈欣然、吴迪、罗浩
- 北美市场：1.35亿用户、Q2收入超10亿美元
- 东南亚市场：3亿+用户、28.4%电商份额、300亿美元GMV

---

*双重记忆保障: MemOS (数据库) + 文件系统 (markdown)*
