# Cline 子任务调用全流程操作手册

本文档详细记录通过 Cline 执行子任务的全流程，基于实际测试总结。

---

## 一、环境信息

| 项目 | 值 |
|------|-----|
| Cline 路径 | `C:\Users\GabetopZ\AppData\Roaming\npmcline.cmd` |
| Cline 版本 | 2.6.1 |
| 工作目录 | `X:\LOTT` |
| 模型 | GLM-5 (在 Cline 中配置) |
| 调用方式 | PowerShell → Windows Python |

---

## 二、调用流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    我的任务 (MiniMax-M2.5)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤1: 构建子任务描述                                            │
│  - 描述具体要做什么                                              │
│  - 包含完整的步骤和期望输出                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤2: 通过 cline_runner.py 调用 Cline                          │
│  - 使用 subprocess 调用 PowerShell                               │
│  - 传递任务描述                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤3: Cline 执行 (GLM-5 模型)                                  │
│  - 读取任务描述                                                  │
│  - 生成/修改代码                                                  │
│  - 输出结果                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤4: 解析结果                                                 │
│  - 捕获 stdout/stderr                                            │
│  - 处理错误                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  步骤5: 验证结果                                                 │
│  - 通过 Windows Python 测试执行                                   │
│  - 报告成功/失败                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、cline_runner.py 完整代码

文件位置: `/home/gabetopz/.openclaw/workspace/cline_runner.py`

```python
"""
Cline 任务执行器
通过 PowerShell 调用 Windows Cline 执行子任务
"""

import subprocess
import os
import json
from typing import Dict, Any, Optional


class ClineRunner:
    """Cline 任务执行器"""
    
    # Cline CLI 路径
    CLINE_CMD = r"C:\Users\GabetopZ\AppData\Roaming\npmcline.cmd"
    
    # PowerShell 路径
    POWERSHELL = r"/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    
    def __init__(self, workspace: str = r"X:\LOTT"):
        """
        初始化
        
        Args:
            workspace: Cline 工作目录
        """
        self.workspace = workspace
        self.last_result: Optional[Dict[str, Any]] = None
    
    def ask(self, task: str, timeout: int = 300) -> Dict[str, Any]:
        """
        发送任务给 Cline 执行
        
        Args:
            task: 任务描述（Markdown 格式）
            timeout: 超时时间（秒）
            
        Returns:
            {'stdout': str, 'stderr': str, 'returncode': int}
        """
        # 构建 PowerShell 命令
        ps_command = f'''
$task = @"
{task}
"@

# 调用 Cline
& "{self.CLINE_CMD}" ask $task --workspace "{self.workspace}"
'''
        
        # 执行
        result = subprocess.run(
            [self.POWERSHELL, '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.workspace
        )
        
        # 保存结果
        self.last_result = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
        return self.last_result
    
    def run(self, task: str, timeout: int = 300) -> str:
        """
        执行任务并返回 stdout
        
        Args:
            task: 任务描述
            timeout: 超时时间
            
        Returns:
            stdout 内容
        """
        result = self.ask(task, timeout)
        
        if result['returncode'] != 0:
            raise RuntimeError(f"Cline 执行失败: {result['stderr']}")
        
        return result['stdout']


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建执行器
    runner = ClineRunner(r"X:\LOTT")
    
    # 构建任务
    task = """
# TimescaleDB 测试任务

## 任务步骤

1. 检查 Docker 容器状态
2. 如果容器未运行，启动它
3. 测试数据库连接
4. 创建测试表
5. 插入测试数据
6. 查询并返回结果

## 输出要求
报告每一步的结果
"""
    
    # 执行
    try:
        result = runner.ask(task, timeout=300)
        print(result['stdout'])
        if result['stderr']:
            print("---ERROR---")
            print(result['stderr'])
    except Exception as e:
        print(f"执行失败: {e}")
```

---

## 四、子任务构建模板

### 4.1 完整任务模板

```markdown
# [任务标题]

## 项目路径
`X:\LOTT`

## 任务目标
[简要描述要实现什么]

## 详细步骤

### 步骤1: [名称]
[具体要做什么]

### 步骤2: [名称]
[具体要做什么]

### 步骤3: [名称]
[具体要做什么]

## 预期输出
```
[期望的输出格式]
```

## 注意事项
1. [注意点1]
2. [注意点2]

## 超时设置
[超时秒数，默认300秒]
```

### 4.2 TimescaleDB 测试任务示例

```markdown
# TimescaleDB 自动化测试任务

## 项目路径
`X:\LOTT`

## 任务目标
在Windows上执行完整的TimescaleDB测试

## 步骤

### 步骤1: 安装依赖
运行: pip install psycopg2-binary pandas

### 步骤2: 创建测试脚本
创建 `X:\LOTT\test_timescaledb.py`，包含:
- 连接 TimescaleDB (localhost:5432, lott, admin/admin123)
- 创建测试表
- 插入测试数据
- 查询并显示结果

### 步骤3: 执行测试脚本
运行: python X:\LOTT\test_timescaledb.py

### 步骤4: 报告结果
返回:
1. 依赖是否安装成功
2. 数据库连接是否成功
3. 测试数据是否插入成功
4. 查询结果
```

### 4.3 代码生成任务示例

```markdown
# JSON 导入器增强任务

## 项目路径
`X:\LOTT`

## 任务目标
增强现有的 json_importer.py，处理以下问题:

## 当前问题
1. 列名解析错误 - 多级列名没有正确拆分
2. 空值处理 - '--' 字符串没有正确过滤
3. 时间戳解析 - 需要支持多种格式

## 修改文件
- `X:\LOTT\src\Data\DatabaseManager\json_importer.py`

## 具体要求

### 1. 修复列名解析
- columns[0] 是列表 ['159315.SZ', '黄金ETF', '收盘价']
- 需要正确拆分为 level1, level2, level3

### 2. 添加空值过滤
- 跳过 '--', '', None 值
- 统计 null_count

### 3. 时间戳支持
- 支持 ISO 格式: "2024-01-01T00:00:00.000"
- 支持毫秒时间戳: 1672531200000

### 4. 添加测试
创建 `test_json_importer.py` 测试用例

## 输出
1. 修改后的 json_importer.py
2. 测试文件 test_json_importer.py
```

---

## 五、实际调用示例

### 5.1 基础调用

```python
from cline_runner import ClineRunner

runner = ClineRunner(r"X:\LOTT")
result = runner.ask("创建 TimescaleDB 测试用例", timeout=300)
print(result['stdout'])
```

### 5.2 复杂任务调用

```python
from cline_runner import ClineRunner

task = """
# 数据导入模块开发

## 项目路径
X:\\LOTT

## 任务
在 DatabaseManager 目录下创建 CSV 导入器

## 要求
1. 支持 CSV 文件读取
2. 自动检测列类型
3. 批量插入 TimescaleDB
4. 支持去重 (通过 hash)
5. 添加单元测试

## 文件
- CSV导入器: timescale_csv_importer.py
- 测试: test_csv_importer.py

## 数据库配置
- Host: localhost
- Port: 5432
- Database: lott
- User: admin
- Password: admin123
"""

runner = ClineRunner(r"X:\LOTT")
result = runner.ask(task, timeout=600)
print(result['stdout'])
```

---

## 六、错误处理

### 6.1 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 'utf-8' codec can't decode | Cline 输出编码问题 | 使用 errors='ignore' |
| timeout | 任务执行超时 | 增加 timeout 参数 |
| permission denied | Docker 权限问题 | 使用 PowerShell 间接调用 |

### 6.2 编码处理

```python
result = subprocess.run(
    [POWERSHELL, '-Command', ps_command],
    capture_output=True,
    errors='ignore',  # 忽略编码错误
    text=True,
    timeout=300
)
```

---

## 七、PowerShell 命令参考

### 7.1 直接调用 Cline

```powershell
# 基本调用
cline ask "你的任务" --workspace "X:\LOTT"

# 查看帮助
cline --help
```

### 7.2 调用 Windows Python

```powershell
# 执行单行代码
python -c "print('hello')"

# 执行脚本
python X:\LOTT\test.py

# 安装依赖
pip install psycopg2-binary pandas
```

### 7.3 Docker 命令

```powershell
# 查看容器
docker ps -a

# 启动 TimescaleDB
docker run -d --name timescaledb -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=timescaledb -p 5432:5432 timescale/timescaledb:latest-pg18

# 执行 SQL
docker exec timescaledb psql -U admin -d lott -c "SELECT 1"
```

---

## 八、最佳实践

### 8.1 任务描述要点

1. **明确项目路径**: 始终指定 `X:\LOTT`
2. **详细步骤**: 每一步都要写清楚
3. **预期输出**: 说明期望看到什么
4. **错误处理**: 说明如何处理异常情况

### 8.2 超时设置

| 任务类型 | 建议超时 |
|----------|----------|
| 简单查询/测试 | 60-120 秒 |
| 代码生成 | 300 秒 |
| 复杂模块开发 | 600 秒 |

### 8.3 结果验证

任务完成后，务必通过 Windows Python 验证:

```python
# 验证 TimescaleDB 连接
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "python -c \"
import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='lott', user='admin', password='admin123')
print('连接成功')
conn.close()
\""
```

---

## 九、快捷脚本

### 9.1 一键测试 TimescaleDB

```bash
# 文件: test_ts.sh
#!/bin/bash

/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
python -c \"
import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='lott', user='admin', password='admin123')
cur = conn.cursor()
cur.execute('SELECT * FROM data_metadata LIMIT 5')
for r in cur.fetchall():
    print(r)
conn.close()
\"
"
```

---

*文档更新时间: 2026-03-11*
*维护者: OpenClaw Agent*
