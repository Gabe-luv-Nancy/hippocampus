# Cline 任务调用模块

## 调用方式

### 方式1: 通过 Windows cmd 调用
```powershell
# 在 PowerShell 或 cmd 中
cline ask "你的任务描述"
```

### 方式2: 通过 Node.js 直接调用
```bash
# 在 PowerShell 中
node C:\Users\GabetopZ\AppData\Roaming\npm\node_modules\cline\dist\cli.mjs ask "任务描述"
```

### 方式3: 通过 Python subprocess 调用
```python
import subprocess

result = subprocess.run(
    ["cmd", "/c", "cline", "ask", "任务描述"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

---

## 可用命令

根据 Cline CLI 文档，主要命令包括：

| 命令 | 说明 |
|------|------|
| `cline ask <prompt>` | 发送一个问题/任务 |
| `cline chat` | 启动交互式聊天 |
| `cline act <file>` | 从文件执行任务 |
| `cline [options]` | 查看帮助 |

---

## 任务文件格式

Cline 读取任务的方式：
1. 任务作为命令行参数
2. 从 stdin 读取
3. 从任务目录的 JSON 文件读取

### 任务目录结构
```
~/.cline/data/tasks/<timestamp>/
├── api_conversation_history.json  # 对话历史
├── task_metadata.json              # 元数据
└── ui_messages.json                # UI 消息
```

---

## 工作流程

### 步骤 1: 创建任务文件
```python
import json
import os
import time

task_id = str(int(time.time() * 1000))
task_dir = os.path.expanduser("~/.cline/data/tasks/" + task_id)
os.makedirs(task_dir, exist_ok=True)

# 创建任务元数据
metadata = {
    "files_in_context": [],
    "model_usage": [],
    "environment_history": []
}

with open(os.path.join(task_dir, "task_metadata.json"), "w") as f:
    json.dump(metadata, f)

# 创建对话历史（用户的第一条消息）
conversation = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "你的任务描述"}
        ],
        "ts": int(time.time() * 1000)
    }
]

with open(os.path.join(task_dir, "api_conversation_history.json"), "w") as f:
    json.dump(conversation, f)
```

### 步骤 2: 执行任务
创建任务后，Cline CLI 应该会自动检测并执行。

---

# Cline + Windows Python 任务调用模块

## 一、Cline 调用方式

### 方式1: 通过 Windows cmd 调用
```powershell
# 在 PowerShell 或 cmd 中
cline ask "你的任务描述"
```

### 方式2: 通过 Node.js 直接调用
```bash
# 在 PowerShell 中
node C:\Users\GabetopZ\AppData\Roaming\npm\node_modules</minimax:tool_call>\dist\cli.mjs ask "任务描述"
```

### 方式3: 通过 Python subprocess 调用
```python
import subprocess

result = subprocess.run(
    ["cmd", "/c", "cline", "ask", "任务描述"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

---

## 二、PowerShell 调用 Windows Python（全流程方案）

### 2.1 核心命令格式

```powershell
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "python -c \"你的Python代码\""
```

### 2.2 完整示例：TimescaleDB 测试

```python
import subprocess

# 构建PowerShell命令
ps_cmd = '''
python -c "
import psycopg2
import json
import hashlib
from datetime import datetime, timezone, timedelta

# 1. 连接数据库
conn = psycopg2.connect(host='localhost', port=5432, database='lott', user='admin', password='admin123')
cur = conn.cursor()

# 2. 清空测试数据
cur.execute('TRUNCATE timeseries_data, data_metadata RESTART IDENTITY CASCADE')
conn.commit()

# 3. 读取JSON文件
with open(r'X:\\LOTT\\src\\Data\\DataSource\\_json\\futures.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 4. 处理数据...

# 5. 插入数据
cur.execute('''INSERT INTO data_metadata ...''')
conn.commit()

# 6. 查询结果
cur.execute('SELECT * FROM data_metadata')
print(cur.fetchall())

conn.close()
print('完成!')
"
'''

# 执行
result = subprocess.run(
    ['/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe', '-Command', ps_cmd],
    capture_output=True,
    text=True,
    timeout=120
)

print(result.stdout)
print(result.stderr)
```

### 2.3 常用命令速查

| 任务 | 命令 |
|------|------|
| 安装依赖 | `pip install psycopg2-binary pandas` |
| 检查Python模块 | `python -c "import psycopg2; print('OK')"` |
| 执行Python脚本 | `python X:\\LOTT\\test.py` |
| Docker检查 | `docker ps --filter 'name=timescaledb'` |
| Docker执行SQL | `docker exec timescaledb psql -U admin -d lott -c "SELECT 1"` |

### 2.4 PowerShell 路径注意

- WSL路径到Windows: `/mnt/c/...`
- Windows路径: `X:\\...` 或 `X:\...`
- 引号嵌套: 外层双引号，内层用 `\"` 或单引号

---

## 三、cline_runner.py 使用方法
```

---

## 注意事项

1. **模型**: Cline 使用 GLM-5（用户配置）
2. **工作目录**: 默认是 `X:\LOTT`
3. **上下文**: 128K 限制
4. **输出**: Cline 会直接修改文件

---

*文档更新时间: 2026-03-11*
