# 记忆系统状态

## 最后更新: 2026-03-11 23:00

### 系统状态

- **MemOS**: ✅ 正常运行 (1个插件已加载, 0个错误)
- **数据库**: ✅ 存在 (253KB, 最后更新: 2026-03-10 23:30)
- **传统记忆文件**: ✅ 12个文件

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
- CORE_AI_INTEGRATION.md
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
*双重记忆保障: MemOS (数据库) + 文件系统 (markdown)*
