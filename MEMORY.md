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
