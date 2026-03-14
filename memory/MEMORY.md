# 记忆系统状态

## 最后更新: 2026-03-14 12:10

### 系统状态

- **MemOS**: ✅ 正常运行 (1个插件已加载, 0个错误)
- **数据库**: ✅ 存在 (253KB, 最后更新: 2026-03-10 23:30)
- **传统记忆文件**: ✅ 13个文件（含今日新增 2026-03-11.md）

### Cron 任务状态

| 任务 | 状态 | 说明 |
|------|------|------|
| memory-backup-check | ✅ 运行中 | 每日早8点检查 |
| memory-check-double | ✅ 运行中 | 双重检查 (当前任务) |
| memory-backup-evening | ⚠️ 错误 | 晚间备份失败 - 需配置 delivery.channel |

### 已知问题

1. **晚间备份任务失败** (2026-03-10)
   - 错误: "Channel is required (no configured channels detected)"
   - 建议: 设置 delivery.channel 或使用 main session

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

### 2026-03-13 日常工作
- **HEARTBEAT 巡检任务**: 执行心跳检查，检查 Gateway 存活状态 (HTTP 200)
- **记忆备份缺失问题**: 发现 2026-03-13.md 备份文件未生成，可能是 cron 备份任务配置问题
- **手动触发备份**: 手动触发记忆备份请求
- **Cron 故障调查**: 调查晚间备份任务失败原因，检查 delivery.channel 配置

### 2026-03-12 日常工作
- **ClawdHub CLI 安装**: 成功安装 ClawdHub CLI (v0.3.0) 用于管理 skills
- **Skills 大规模安装**: 从 Downloads 目录解压安装21个 skills
- **Hooks 讨论**: 解释4个已安装 hooks 的用途（全部 ✓ ready 状态）
- **Cron 任务故障**: 晚间记忆备份任务因 delivery.channel 未配置持续失败 🔴

### 2026-03-11 日常工作
- **公司登记表单分析**: 分析微信图片提取24个字段，生成 xlsx/csv 文件
- **LO TT TimescaleDB 集成**: 创建 timescaleDB 配置、连接、表结构、JSON导入器等6个文件
- **Cline 集成环境配置**: 创建 cline_runner.py，配置 Windows Cline 调用（CLI路径已记录）
- **重要警告**: 禁止使用 GLM-5，所有代码生成必须通过 Cline 执行

### 火山引擎研究报告 (2026-03-10)
- 字节跳动高管团队：梁汝波、周受资、张楠、陈熙、刘思齐、朱骏
- 火山引擎管理团队：谭待（百度背景）、张鑫、陈欣然、吴迪、罗浩
- 北美市场：1.35亿用户、Q2收入超10亿美元
- 东南亚市场：3亿+用户、28.4%电商份额、300亿美元GMV

---

## 重要笔记

### API配置
- Minimax 正确模型：`MiniMax-M2.5-highspeed`
- 端点：`https://api.minimaxi.com/v1`

### 数据采集
- SHFE: AkShare 可用，数据到2026-02-13
- DCE: 有瑞数反爬，浏览器模拟也困难
- CZCE/CFFEX: 需要其他数据源

### Git/备份
- GitHub push 有时超时（443端口不稳定）
- 本地领先时需要 rebase 后再 push

---

### 记忆文件列表

- 2026-02-27.md
- 2026-03-05.md
- 2026-03-10.md
- 2026-03-11.md
- 2026-03-12.md ← 补做（cron 故障后手动创建）
- 2026-03-13.md ← 补做（今日发现未提交）
- CORE_AI_INTEGRATION.md
- **CLINE_SUBTASK_GUIDE.md** ← 重要！Cline调用全流程
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

---

## 📌 每日必读

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

### TimescaleDB 模块
**目录**: `X:\LOTT\src\Data\DatabaseManager\`

| 文件 | 用途 |
|------|------|
| timescale_config.py | 配置 |
| timescale_connection.py | 连接管理 |
| timescale_tables.py | 表结构 |
| json_importer.py | JSON导入 |
| timescale_examples.py | 示例 |

**数据库**: localhost:5432, lott, admin/admin123

---
*双重记忆保障: MemOS (数据库) + 文件系统 (markdown)*
