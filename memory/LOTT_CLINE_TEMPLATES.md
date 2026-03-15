# LOTT 项目 Cline 提示词模板集

本文档包含常用的 Cline 提示词模板，可在 VS Code 中直接复制使用。

---

## 模板 1: 创建新模块

```markdown
# 代码生成任务

## 项目路径
`X:\LOTT`

## 任务目标
[简要描述要实现的功能]

## 技术要求
1. 编程语言: Python 3.x
2. 代码风格: PEP8，项目现有风格保持一致
3. 依赖包: 如需新包请列出，我会添加到 requirements.txt

## 功能规格

### 模块: [模块名称]
- 文件路径: `src/[路径]/[模块名].py`
- 功能描述: [详细描述]
- 类/函数:
  - `class/function name`: [用途]
  - 参数: [类型和说明]
  - 返回值: [类型和说明]

### 辅助函数:
- [列出需要的辅助函数]

## 数据结构

### 输入数据格式
```python
[示例]
```

### 输出数据格式
```python
[示例]
```

## 测试要求
1. 使用 pytest 编写测试
2. 测试文件: `tests/test_[模块名].py`
3. 包含:
   - 单元测试
   - 边界条件测试
   - 错误处理测试

## 输出要求
1. 完整代码实现
2. 测试文件
3. 如需配置变更，说明需要修改的文件
```

---

## 模板 2: Bug 修复

```markdown
# Bug 修复任务

## 项目路径
`X:\LOTT`

## Bug 标题
[简短描述]

## Bug 详细描述
[详细说明问题]

## 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 预期行为
[应该怎样]

## 实际行为
[实际怎样]

## 错误信息
```
[粘贴错误信息]
```

## 相关代码位置
- 文件: `src/xxx/xxx.py`
- 函数: `function_name`
- 行号: ~Line 100

## 修复要求
1. 保持代码风格一致
2. 添加回归测试防止再次发生
3. 修复后运行现有测试确保无破坏
```

---

## 模板 3: 数据源集成

```markdown
# 数据源集成任务

## 项目路径
`X:\LOTT`

## 任务目标
将 [数据源名称] 集成到 LOTT 数据服务层

## 现有架构参考
- 数据源基类: `src/Data/DataSource/`
- 配置管理: `src/Data/DataSource/xxx/config.py`
- 客户端: `src/Data/DataSource/xxx/client.py`

## 技术规格

### 数据源信息
- 类型: [REST API / WebSocket / 数据库 / 文件]
- 连接地址: [URL 或连接字符串]
- 认证方式: [API Key / OAuth / 用户名密码]
- 频率限制: [如有]

### 数据格式
#### 订阅数据
```json
[JSON 示例]
```

#### K线数据字段映射
| 源字段 | 目标字段 | 类型 |
|--------|----------|------|
| symbol | symbol | string |
| ... | ... | ... |

### 需要实现的功能
1. [ ] 连接管理
2. [ ] 数据订阅
3. [ ] 断线重连
4. [ ] 数据转换
5. [ ] 错误处理

## 配置要求
在 `timescaledb_config.yaml` 中添加:
```yaml
[配置示例]
```

## 测试要求
1. Mock 测试数据源响应
2. 集成测试（如可行）
3. 性能测试（数据吞吐量）

## 输出
1. 客户端代码: `src/Data/DataSource/[名称]/client.py`
2. 配置类: `src/Data/DataSource/[名称]/config.py`
3. 测试: `tests/test_[名称]/
```

---

## 模板 4: TimescaleDB 集成

```markdown
# TimescaleDB 集成任务

## 项目路径
`X:\LOTT`

## 背景
已有基础代码在: `src/Data/DataSource/TimescaleDB/`
- config.py: 配置类
- client.py: 数据库客户端
- timescaledb_config.yaml: 配置文件

## 任务目标
[选择一项或多项]

### 选项 1: 创建测试用例
为现有的 TimescaleDB 客户端创建 pytest 测试:
- 文件: `tests/test_timescaledb_client.py`
- 覆盖: 连接、插入、查询、统计

### 选项 2: 集成到数据服务
将 TimescaleDB 客户端集成到现有数据服务:
- 修改 `src/Data/DataService/service.py`
- 添加 TimescaleDB 作为可选数据源

### 选项 3: 数据迁移脚本
将现有 CSV/JSON 数据迁移到 TimescaleDB:
- 源: `data/xxx/`
- 目标: TimescaleDB
- 脚本: `scripts/migrate_to_timescaledb.py`

### 选项 4: Notebook 示例
创建 Jupyter Notebook 使用示例:
- 文件: `notebooks/timescaledb_demo.ipynb`
- 内容: 连接、插入、查询、可视化

## 当前数据库状态
- Docker 容器: 运行中
- 连接: localhost:5432
- 数据库: timescaledb
- 用户: admin / admin123

## 要求
1. 代码风格保持一致
2. 添加必要的错误处理
3. 包含使用文档注释
```

---

## 模板 5: 完整功能模块创建

```markdown
# 完整功能模块创建

## 项目路径
`X:\LOTT`

## 模块名称
[如: 策略信号管理模块]

## 模块概述
[1-2 句话描述这个模块做什么]

## 目录结构
```
src/[模块路径]/
├── __init__.py
├── config.py          # 配置类
├── client.py         # 主要客户端
├── models.py         # 数据模型
├── service.py        # 业务逻辑
└── exceptions.py     # 自定义异常
```

## 功能列表

### F1: [功能名称]
- 描述: [做什么]
- 输入: [参数]
- 输出: [返回值]
- 边界: [边界条件]

### F2: [功能名称]
- ...

## 数据模型

### ModelName
| 字段 | 类型 | 说明 |
|------|------|------|
| field1 | str | 说明 |
| field2 | int | 说明 |

## 接口设计

```python
class Client:
    def method1(self, param: Type) -> ReturnType:
        '''文档字符串'''
        pass
```

## 依赖
```txt
[列出需要的 pip 包]
```

## 测试要求
- 文件: `tests/test_[模块]/*.py`
- 覆盖率: > 80%
- 包含: 单元测试、集成测试

## 文档要求
- 模块级 README.md
- 关键函数 docstring

---

## 使用说明

1. **打开 Cline**: 在 VS Code 中按 `Ctrl+Shift+P`，输入 "Cline: New Conversation"
2. **复制模板**: 选择合适的模板，填入具体需求
3. **执行**: Cline 会生成代码
4. **测试**: 运行 `pytest X:\LOTT\tests\`
5. **复核**: 检查代码是否符合要求
```

---

*模板版本: 2026-03-11*
