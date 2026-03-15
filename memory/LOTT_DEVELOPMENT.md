# LOTT 项目开发环境与工作流程记忆 (更新版)

## 一、环境架构

### 1.1 系统架构
```
┌─────────────────────────────────────────────────────────────┐
│                     Windows 主机 (X:)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │  VS Code    │  │  Docker     │  │  Cline (GLM-5)  │    │
│  │  + Cline    │  │  Desktop    │  │  CLI: cline    │    │
│  │  插件        │  │  TimescaleDB│  │  路径:         │    │
│  │             │  │             │  │  %APPDATA%/npm │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
│         │                │                    │              │
│         └────────────────┼────────────────────┘              │
│                          │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │              WSL 2 (Ubuntu 24.04) - 我的环境        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  OpenClaw   │  │  Python     │  │  Cline     │  │   │
│  │  │  Agent      │  │  3.12       │  │  Runner    │  │   │
│  │  │  (MiniMax)  │  │             │  │  Script    │  │   │
│  │  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 关键路径
| 资源 | Windows 路径 | WSL 路径 |
|------|-------------|----------|
| LOTT 项目 | `X:\LOTT` | `/mnt/x/LOTT` |
| Cline CLI | `C:\Users\GabetopZ\AppData\Roaming\npm\cline.cmd` | 通过 cmd 调用 |
| Cline 数据 | `C:\Users\GabetopZ\.cline\data\` | `/mnt/c/Users/gabetopz/.cline/data/` |
| 任务目录 | `C:\Users\GabetopZ\.cline\data\tasks\` | `/mnt/c/Users/gabetopz/.cline/data/tasks/` |
| OpenClaw | `%USERPROFILE%\.openclaw` | `/home/gabetopz/.openclaw` |

---

## 二、模型配置

### 2.1 模型分工
| 场景 | 模型 | 位置 | 状态 |
|------|------|------|------|
| 我 (主对话) | MiniMax-M2.5 | 我的配置 | ✅ 稳定 |
| 代码生成 | GLM-5 | Cline 插件 | ✅ 用户配置 |

### 2.2 重要警告 ⚠️
- **禁止将 GLM-5 添加到我的配置** - 智谱 API 不稳定
- 所有代码生成任务必须通过 Cline (GLM-5) 执行
- 我负责任务分解、提示词编写、结果复核、测试

---

## 三、Cline 调用方式

### 3.1 Cline CLI 位置
```
C:\Users\GabetopZ\AppData\Roaming\npm\cline.cmd
```

### 3.2 在我的环境中调用 Cline
我可以通过以下方式调用 Cline：

1. **命令行调用** (通过 cmd):
   ```bash
   cmd /c "cline ask '任务描述'"
   ```

2. **Python 脚本调用**:
   - 文件: `/home/gabetopz/.openclaw/workspace/cline_runner.py`
   - 使用方法:
   ```python
   from cline_runner import run_cline_task
   
   result = run_cline_task("创建 TimescaleDB 测试用例")
   ```

3. **任务文件方式**:
   - 在 `~/.cline/data/tasks/<timestamp>/` 创建任务目录
   - 写入 `api_conversation_history.json`
   - Cline 会自动检测并执行

---

## 四、工作流程

### 4.1 任务执行流程
```
用户需求
    │
    ▼
┌─────────────────────────────────────────┐
│  我 (MiniMax-M2.5)                      │
│  1. 需求分析                            │
│  2. 拆解功能模块                        │
│  3. 生成 Cline 提示词                   │
└────────────────┬────────────────────────┘
                 │
    ▼ (调用 Cline)
┌─────────────────────────────────────────┐
│  Cline (GLM-5)                         │
│  4. 生成代码                            │
│  5. 写入 X:\LOTT                       │
└────────────────┬────────────────────────┘
                 │
    ▼
┌─────────────────────────────────────────┐
│  我 (复核)                              │
│  6. 检查代码语法                        │
│  7. 验证逻辑正确性                      │
│  8. 运行测试                            │
└────────────────┬────────────────────────┘
                 │
    ▼ (如有问题)
┌─────────────────────────────────────────┐
│  循环调整                               │
│  - 分析问题                             │
│  - 生成修复提示词                       │
│  - 新 Cline 对话执行                    │
└─────────────────────────────────────────┘
```

### 4.2 上下文管理
- **128K 限制**: 复杂任务可能占满
- **解决方案**: 
  - 每个子任务独立 Cline 对话
  - 我只保留任务分解和复核结果
  - 不保留完整代码在对话中

---

## 五、提示词模板位置

| 文件 | 说明 |
|------|------|
| `memory/LOTT_CLINE_TEMPLATES.md` | Cline 提示词模板集 |
| `memory/LOTT_DEVELOPMENT.md` | 完整开发流程 |
| `memory/LOTT_QUICKREF.md` | 快速参考 |

---

## 六、测试框架

### 6.1 测试工具
| 工具 | 用途 | 状态 |
|------|------|------|
| pytest | Python 单元测试 | WSL 中受限 |
| Playwright | 端到端测试 | WSL 中受限 |
| Cline | 代码生成 + 测试 | Windows |

### 6.2 安装脚本
由于 WSL 环境限制，测试框架安装由 Cline 执行：
```python
# Cline 提示词示例
"""
在 X:\LOTT 环境中:
1. 安装 pytest: pip install pytest
2. 安装 Playwright: pip install playwright
3. 运行测试: pytest X:\LOTT\tests\ -v
"""
```

---

## 七、常用命令

### 7.1 我 (WSL)
```bash
# 查看 LOTT 项目
ls -la /mnt/x/LOTT/

# 读取文件
cat /mnt/x/LOTT/src/Data/DataSource/TimescaleDB/README.md

# 调用 Cline
cmd /c "cline ask '你的任务'"
```

### 7.2 你 (Windows + Cline)
```bash
# Cline 快捷键
Ctrl+Shift+P -> Cline: New Conversation

# 常用命令
conda activate LOTT
pytest tests/
```

---

## 八、注意事项

1. **不要修改我的配置** - 不添加 GLM-5
2. **使用子任务管理** - 复杂任务拆分执行
3. **测试驱动** - 每次代码变更测试验证
4. **上下文管理** - 长任务多轮对话
5. **结果复核** - Cline 代码必须检查

---

*最后更新: 2026-03-11*
