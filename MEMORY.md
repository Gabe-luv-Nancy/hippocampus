# MEMORY.md - Long-Term Memory

## Deployment & Security

- **Platform:** Windows laptop via WSL Ubuntu
- **Key rule:** Don't touch Windows system files or WSL config files that affect my process
- **Safe to edit:** Project files, engineering files (with backups)
- **When in doubt:** Ask first

## Preferences (Gabe's)
- Communication: Pleasant + efficient, no fluff
- Humor welcome when it fits naturally
- Research-first: substantive, no boilerplate
- Call me: bro or Gabe

## Contact
- Timezone: GMT+8 (Asia/Shanghai)

## 系统架构

### Windows + WSL2 + Ubuntu 关系
```
Windows (宿主系统)
│
├── VS Code + CLINE 插件 ←── Gabe 在这里编程
│
└── WSL2 (虚拟化层)
    │
    └── Ubuntu 24.04 ←── OpenClaw (Dude) 在这里运行
```

**简短说法：**
> WSL2 是 Windows 的 Linux 兼容层，Ubuntu 是运行其中的 Linux 发行版。两者共享文件系统（Windows 盘挂载在 `/mnt/`），但各自有独立的环境。

### 调用方式
- 我在 WSL 中，通过 `/mnt/c/Users/Gabe/AppData/Roaming/npm/cline.cmd` 调用 Windows 上的 CLINE CLI
- LOTT 工程在 Windows: `X:\LOTT` (WSL 路径: `/mnt/x/LOTT`)

### CLINE CLI 配置
- **安装路径**: `C:\Users\GabetopZ\AppData\Roaming\npm\cline`
- **版本**: 2.6.1
- **模型**: GLM-5 (zai/glm-5) 通过硅基流动 API
- **Node.js**: v24.14.0 (Windows)
- **调用方式**: 用户在 PowerShell 中运行 `cline` 命令

### CLINE CLI JSON 输出格式
```json
{"type":"task_started","taskId":"..."}           // 任务开始
{"ts":...,"type":"say","say":"text","text":"..."} // 文本响应
{"ts":...,"type":"say","say":"tool","text":"{...}"} // 工具调用
{"ts":...,"type":"say","say":"task_progress","text":"..."} // 任务进度
```
- 流式输出，每行一个 JSON 对象
- 支持工具: searchFiles, read_file 等

## API & Models

### 硅基流动 API
- **API Key:** `sk-hgkxpbbusfstcyverghkfmljybhpnvpsxedisydtrhigwbro`
- **用途:** 语音识别 (STT) + 视觉理解 (VLM)
- **可用模型:** QVQ-72B-Preview, Qwen2-VL-72B-Instruct, MiniMax-M2.5

### API 安全规则 ⚠️ 2026-02-27 事故教训
- 🚫 **绝对禁止**直接修改 models.json — 会导致 OpenClaw 无法启动！
- 🚫 **绝对禁止**在 models.json 中添加硅基流动模型配置
- ✅ **正确方式**: 使用独立脚本 + 子任务调用硅基流动 API
- ✅ 如需调用 VLM/STT：启动子任务执行脚本，返回结果或报错
- ✅ 脚本出错不会影响主进程，安全可控

## 服务稳定性

### 风险分级
- 🔴 高危: 修改models.json、重启gateway、修改飞书配置
- 🟡 中危: 安装新插件、添加新模型
- 🟢 低危: 修改memory文件、更新文档

### 心跳检查 (必须执行)
- 每1小时检查 Gateway 存活状态
- 检查本地快照数量
- 检查 API 连通性
- 异常则告警 + 尝试恢复

### 四重保障
1. 执行前强制备份
2. 沙盒环境测试
3. 心跳监控保命
4. 快速回滚机制

## 备份
- 仓库: Gabe-luv-Nancy/MyBroOpenClaw
- 频率: 每周日 21:00 Asia/Shanghai
- 源: MEMORY.md + memory/*.md

## 数据库配置

### PostgreSQL + TimescaleDB
- **安装路径**: `C:\Program Files\PostgreSQL\18`
- **Port**: 5432
- **超级用户密码**: 1211
- **TimescaleDB 源码**: `X:\LOTT\ref\timescaledb-main`
- **用途**: 时序数据存储，宽表 + 元数据

### Redis
- **源码路径**: `X:\LOTT\ref\redis-unstable`
- **用途**: 实时消息分发、缓存

## SimNow 数据收集

### 脚本位置
- `X:\LOTT\simnow_collector.py` - 行情收集脚本
- 运行命令: `PYTHONPATH="/mnt/x/LOTT/conda/Lib/site-packages:$PYTHONPATH" /mnt/x/LOTT/conda/python.exe simnow_collector.py`

### 定时任务
- 每天早上 8:55 (周一到周五) 自动启动
- 数据写入: `X:\LOTT\src\Data\DataSource\_db\realtime\simnow.db`

### SimNow 账户
- 用户名: 13021081780
- 密码: Lottgoeswell0308$
- 经纪商: 9999

## 2026-03-05 更新

### 模型切换
- ✅ 默认模型从 **MiniMax-M2.5-Lightning** 切换为 **MiniMax-M2.5-highspeed**
- 原因: Lightning 价格贵 50 倍 (15 vs 0.3)，M2.5-highspeed 性价比更高，深度推理能力相同
- 操作: 修改 `openclaw.json` 中的 agents.defaults.model.primary
- MiniMax 自动补充了 models.json (非手动添加)

### 工作规范
- 🔒 修改 openclaw.json 比修改 models.json 更安全
- 🔒 任何模型配置修改前先备份
- 🔒 改完重启 Gateway 生效

### 新建技能
1. **config-safe-modify** - 配置文件安全修改（备份+验证+回滚）
2. **semantic-model-router** - 语义识别智能选模型
3. **complex-task-methodology** - 复杂任务方法论
4. **automated-testing** - 自动化测试（CLI + Browser UI）

### LOTT 工程
- 开始代码工程，准备自动化测试能力

## 研究与执行 Know-How

### 子任务 vs 直接执行
- **使用子任务场景**:
  - 复杂多步骤任务（如研报生成需要读取多份文件）
  - 需要并行处理多个独立任务
  - 长时间运行的任务
  - 可能超时或失败的探索性任务
- **直接执行场景**:
  - 简单文件操作
  - 快速检查（如心跳检查）
  - 单次API调用

### 网络工具限制
- **web_search**: 需要 Brave API key（`openclaw configure --section web`）
- **web_fetch**: 轻量级页面获取，无需认证
- **无头浏览器**: 复杂反爬场景使用 browser 工具
- **Chrome Relay**: 需要用户手动 Attach Tab，适合需要登录的反爬网站

### 搜索技巧
- 英文搜索有时比中文更有效
- 多尝试不同关键词组合
- 学术/研报类内容优先搜索标题+PDF

### Git 操作
- GitHub push 有时超时（443端口不稳定），本地领先时可先 rebase
- 重要更改后及时 commit，避免堆积

### 数据采集经验
- **SHFE期货**: AkShare 可用，数据较完整
- **DCE**: 有瑞数反爬，浏览器模拟困难
- **CZCE/CFFEX**: 需要其他数据源或模拟浏览器

## 2026-03-10 更新

### 记忆备份 Cron（双重保障）
| 时间 | 任务 |
|------|------|
| 23:00 | daily-memory-backup - 主动备份记忆 |
| 00:00 | memory-backup-check - 检查昨天备份 |

### 火山引擎研报任务
- 用户要求详细高管履历（每人单独）、分国家区域分析
- 删除风险章节，结论只留概括要点
- 子任务并发限制5个，注意任务调度

### Word文档更新教训
- 问题：更新Word文档时内容丢失（47KB→18KB）
- 原因：Python docx库处理复杂文档时可能丢内容
- 教训：复杂文档用markdown管理，更新前必须备份

### Word文档生成经验
- 问题：直接调用python-docx失败（ModuleNotFoundError）
- 解决：使用子任务（sessions_spawn）调用python-docx生成Word
- 子任务中可以正确import docx模块并生成文档
- 注意：markdown内容需先存为文件，子任务读取后转换

### Chrome Relay 配置
- **Gateway Token位置**: `~/.openclaw/openclaw.json` → `gateway.auth.token`
- **当前Token**: `f8436e6580b68280db9d0867f0ed3e79f49d5f4ba34310c3`
- **Token特性**: 固定不变，重启Gateway保持一致
- **WSL限制**: WSL检测不到Windows Chrome，需用Chrome扩展连接
- **扩展配置**: WebSocket URL + Token

## 2026-03-12 问题记录

### Cron 记忆备份任务故障 🔴
- **问题**: 记忆备份 cron 任务持续失败
- **错误信息**: "Channel is required (no configured channels detected). Set delivery.channel explicitly or use a main session with a previous channel."
- **受影响任务**:
  - `memory-backup-evening` (23:00) - 连续2次错误
  - `memory-backup-check` (00:00) - 连续2次错误
  - `memory-check-double` (08:00) - 当前运行中但状态error
- **原因分析**: delivery.mode 设为 "announce" 但未配置 channel
- **解决方案**: 需要修改 cron job 配置，添加 delivery.channel 或改用 main session
