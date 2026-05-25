---
name: answersheet
version: "1.0"
description: "AnswerSheet 可验证填表明文范式 — 创建、填写、验证、归纳"
category: productivity
---

# AnswerSheet Skill

> 一种纯明文的可验证填表格式，以 `.md` 文件为载体。
> 核心产物是 Markdown 文件本身，不是软件系统。

**工作台**: `/mnt/x/CLABIN/HIPPO/AnswerSheet/`
**规范**: `SPEC.md` (v1.0, 含 EBNF 语法)
**引擎**: `src/answersheet.py` (Parser + Validator + Filler + InductionEngine)
**CLI**: `src/cli.py` (5 个子命令)
**测试**: `tests/test_core.py` (23 个, 全通过)

---

## 1. 文件结构概览

每个 AnswerSheet `.md` 文件由三部分组成：

```
┌─────────────────────────────┐
│  ① YAML Front Matter        │  ← modules（角色权限）+ 元数据
├─────────────────────────────┤
│  ② Markdown 正文             │  ← 含 {{ slot:xxx | ... }} 填空位
├─────────────────────────────┤
│  ③ 答案区（可选）             │  <!-- answers --> 之后，有监督模式专用
└─────────────────────────────┘
```

---

## 2. 角色使用指南

### 2.1 创建者（creator）— 怎么创建一张 AnswerSheet

创建者的职责：**定义表单结构、分配角色权限、设置验证规则、存放标准答案**。

#### 步骤一：写 Front Matter

```yaml
---
answersheet: "1.0"
title: "学生考试成绩单"
modules:
  - name: teacher
    role: creator
    description: "出卷教师，创建答案"
  - name: student
    role: filler
    description: "答题学生，填写信息"
  - name: admin
    role: reviewer
    description: "管理员，审核"
created: "2026-05-14"
---
```

**要点**：
- `answersheet: "1.0"` 是格式标识，必须
- `modules` 里定义所有参与角色，每个 module 有唯一的 `name`
- 角色类型：`creator`（创建者）、`filler`（填写者）、`reviewer`（审核者）
- module 的 `name` 就是后续 slot 绑定的权限标识

#### 步骤二：写正文 + 布置 Slot

Slot 是填空位，语法：

```
{{ slot:<名称> | module=<谁有权填> [, verify=<验证模式>] [, rule=<规则>] }}
```

**示例**：

```markdown
# 学生考试成绩单

## 基本信息（学生填写）
学生姓名：{{ slot:student_name | module=student }}
学号：{{ slot:student_id | module=student }}

## 考试成绩（教师填写，有监督验证）
语文：{{ slot:chinese_score | module=teacher, verify=supervised }}
数学：{{ slot:math_score | module=teacher, verify=supervised }}

## 教师评语（教师填写，归纳验证）
{{ slot:comment | module=teacher, verify=induction, rule=pattern:"^.{10,200}$" }}
```

**权限分配规则**：
- `module=student` → 只有 student 角色能填这个空
- `module=teacher` → 只有 teacher 角色能填这个空
- 每个 slot 必须绑定一个 module，没有"任何人都能填"的 slot

**验证模式选择**：
- 你知道标准答案 → 用 `verify=supervised`（在答案区预存哈希）
- 没有标准答案但有规则约束 → 用 `verify=induction` + `rule=...`
- 不需要验证 → 省略 verify（默认 supervised 但不存答案则不检查）

#### 步骤三：设置验证规则（归纳模式专用）

4 种规则类型：

| 类型 | 格式 | 适用场景 | 例子 |
|------|------|---------|------|
| `pattern` | `pattern:"<regex>"` | 格式约束 | `pattern:"^\\d{4}-\\d{2}-\\d{2}$"` |
| `range` | `range:<min>-<max>` | 数值范围 | `range:0-100` |
| `enum` | `enum:<v1>,<v2>,...` | 固定选项 | `enum:是,否,待定` |
| `length` | `length:<min>-<max>` | 长度约束 | `length:5-500` |

**例子**：
```markdown
年龄段：{{ slot:age_group | module=user, verify=induction, rule=enum:18-25,26-35,36-45 }}
满意度：{{ slot:score | module=user, verify=induction, rule=range:1-10 }}
反馈：{{ slot:feedback | module=user, verify=induction, rule=length:10-500 }}
```

#### 步骤四：存放标准答案（有监督模式）

在文件末尾加答案区：

```markdown
<!-- answers -->
[chinese_score]: plain:92
[math_score]: sha256:a3f7b2c1d4e5f6...
```

| 类型 | 格式 | 安全级别 | 适用场景 |
|------|------|---------|---------|
| `sha256` | `sha256:<hex>` | 🔴 高 | 生产环境，填写者无法反推答案 |
| `md5` | `md5:<hex>` | 🟡 中 | 轻量验证 |
| `plain` | `plain:<明文>` | 🟢 测试 | 开发/测试阶段 |

#### 完整创建示例

```markdown
---
answersheet: "1.0"
title: "学生考试成绩单"
modules:
  - name: teacher
    role: creator
  - name: student
    role: filler
created: "2026-05-14"
---

# 学生考试成绩单

姓名：{{ slot:name | module=student }}
语文：{{ slot:chinese | module=teacher, verify=supervised }}
评语：{{ slot:comment | module=teacher, verify=induction, rule=pattern:"^.{5,200}$" }}

<!-- answers -->
[chinese]: plain:95
```

---

### 2.2 填写者（filler）— 怎么填写

填写者只能操作 **分配给自己 module** 的 slot。

#### CLI 方式

```bash
cd /mnt/x/CLABIN/HIPPO/AnswerSheet/src

# 以 student 身份填写
python cli.py fill ../form.md -s name -v "张三"
python cli.py fill ../form.md -s student_id -v "2024001"

# 以 teacher 身份填写
python cli.py fill ../form.md -s chinese -v "92"
```

#### Agent 方式（Python API）

```python
import sys
sys.path.insert(0, '/mnt/x/CLABIN/HIPPO/AnswerSheet/src')
from answersheet import AnswerSheetFiller, parse_file, AnswerSheetValidator

# 读取文件
with open('form.md', 'r') as f:
    content = f.read()

# 填充
filler = AnswerSheetFiller()
content = filler.fill(content, 'name', '张三')
content = filler.fill(content, 'student_id', '2024001')

# 写回
with open('form.md', 'w') as f:
    f.write(content)
```

**填写后的文件变化**：
```markdown
# 填写前
姓名：{{ slot:name | module=student }}

# 填写后
姓名：{{ slot:name | module=student | value=张三 }}
```

---

### 2.3 审核者/验证者（reviewer）— 怎么验证

#### CLI 验证

```bash
# 全文验证
python cli.py validate ../form.md

# 以特定 module 身份验证（只检查属于自己的 slot）
python cli.py validate ../form.md -m student

# 验证单个 slot
python cli.py verify ../form.md chinese

# 查看文件结构
python cli.py info ../form.md
```

#### Agent 验证

```python
from answersheet import parse_file, AnswerSheetValidator

sheet = parse_file('form.md')

# 全量验证
validator = AnswerSheetValidator()
result = validator.validate(sheet)
# result = {"valid": True/False, "errors": [...], "warnings": [...]}

# 以 student 身份验证（只检查 student 的 slot）
result = validator.validate(sheet, actor_module="student")

# 查看详情
for slot in sheet.slots:
    print(f"{slot.name}: value={slot.value}, verify={slot.verify.value}")
```

#### 验证输出解读

```
✅ 验证通过          → 所有已填写的 slot 都通过了验证
❌ 验证失败          → 有 slot 填错了（哈希不匹配 / 不符合规则）
⚠️ slot 'xxx' 尚未填写 → 还有空没填（不算错误）
```

---

### 2.4 归纳者 — 从多份表归纳规则

当收集了多份已填表，可以从同一个 slot 的值中自动归纳出验证规则：

```bash
# 自动归纳（从10份调研表中的 satisfaction slot）
python cli.py induce satisfaction survey1.md survey2.md ... survey10.md

# 指定规则类型
python cli.py induce satisfaction survey1.md survey2.md -t range
```

```python
from answersheet import InductionEngine

engine = InductionEngine()
rule = engine.induce(["92", "88", "95", "90", "87"], rule_type="auto")
# → "range:87.0-95.0"

rule = engine.induce(["是", "否", "是", "待定"], rule_type="auto")
# → "enum:否,是,待定"
```

---

## 3. 权限机制详解

### 3.1 当前 v1.0 的权限模型：声明式

```
┌───────────────────────────────────────────┐
│  YAML Front Matter                        │
│    modules: [teacher, student, admin]      │  ← 声明有哪些角色
│                                            │
│  Slot 绑定                                 │
│    {{ slot:name | module=student }}        │  ← 每个 slot 绑定一个角色
│    {{ slot:score | module=teacher }}       │
│                                            │
│  验证时                                    │
│    validator.validate(sheet, actor_module) │  ← 传入角色身份，只检查属于该角色的 slot
└───────────────────────────────────────────┘
```

**v1.0 的权限保证**：
- ✅ 每个 slot 明确声明了谁有权填写
- ✅ 验证器支持按 module 过滤检查
- ✅ 格式本身是可审计的——任何人打开文件都能看到权限声明
- ⚠️ **但是**：这是"君子协定"，依赖使用者和 Agent 自觉遵守 module 边界

### 3.2 为什么 v1.0 不需要编译层创新

| 层级 | 能力 | AnswerSheet 需要？ |
|------|------|-------------------|
| 编译层 / OS 层 | 内存保护、进程隔离、Ring 权限环 | ❌ 过重，违背"纯明文零依赖"原则 |
| 密码学层 | 签名验证、篡改检测、身份证明 | ✅ **正解** |
| 协议层 | TLS、OAuth 等 | 辅助，非核心 |

AnswerSheet 的本质是**明文协议**，不是操作系统。它的权限保障不需要也不应该依赖编译器或 OS 内核。正确路径是**密码学层**。

### 3.3 v1.1 规划：密码学签名增强

为每个 module 的填写追加数字签名，实现**可验证的权限强制执行**：

```
扩展前（v1.0）:
{{ slot:score | module=teacher | value=95 }}

扩展后（v1.1）:
{{ slot:score | module=teacher | value=95 | sig=ed25519:a3f7... }}
```

**签名流程**：
1. 每个 module 持有一对 Ed25519 密钥（公钥存在 front matter）
2. 填写时用私钥对 `slot名+值` 签名，签名附加到 slot
3. 验证时用公钥校验签名 → 签名不匹配 = 越权操作

**安全效果**：
- student 试图填 teacher 的 slot → 没有 teacher 的私钥 → 签名校验失败
- 任何人篡改已填的值 → 原签名校验失败
- 创建者篡改答案区 → 创建者签名校验失败

**这个扩展完全兼容 v1.0 格式**，`sig` 是可选字段，旧文件不加签名也能用。

---

## 4. 错误码速查

| 错误码 | 含义 | 常见原因 |
|--------|------|---------|
| E001 | front matter 格式错误 | 缺少 `---` 包裹，YAML 语法错 |
| E002 | 缺少必填字段 | 缺 `answersheet`/`title`/`modules` |
| E003 | slot 语法错误 | 格式不对、参数拼写错 |
| E004 | module 未定义 | slot 引用了 modules 里没有的名字 |
| E005 | 有监督验证失败 | 填写值与答案哈希不匹配（填错了） |
| E006 | 归纳验证失败 | 值不符合 rule（超范围、不匹配正则等） |
| E007 | 答案区格式错误 | 答案行格式不对 |
| E008 | slot 未填写 | 还有空没填 |
| E009 | slot 名称重复 | 两个 slot 用了同一个 name |

---

## 5. Pitfalls（坑）

- **PyYAML 是唯一外部依赖**：`import yaml` 需要 PyYAML。通常已安装，如果没有：`pip install pyyaml`
- **CLI 要在 src/ 目录下运行**：因为 `cli.py` 用 `from answersheet import ...`，需要从 `src/` 目录执行，或把 `src/` 加到 `PYTHONPATH`
- **slot 名称只能用字母数字下划线**：`slot:student_name` ✅，`slot:学生姓名` ❌
- **答案区的 slot 名要加方括号**：`[chinese_score]: plain:92` ✅，`chinese_score: plain:92` ❌
- **induction 规则的 regex 要转义**：YAML 里写 `rule=pattern:"^\\d+$"` 双反斜杠
- **plain 答案是明文存储**：仅用于测试，生产环境必须用 `sha256` 或 `md5`
- **induction 归纳至少需要 2 个实例**：只有 1 个值无法归纳出有意义的规则

---

## 6. 快速命令参考

```bash
# 设置路径
AS=/mnt/x/CLABIN/HIPPO/AnswerSheet

# 查看表单结构
python $AS/src/cli.py info $AS/examples/sample-supervised.md

# 填写
python $AS/src/cli.py fill form.md -s student_name -v "张三"

# 全文验证
python $AS/src/cli.py validate form.md

# 验证单个 slot
python $AS/src/cli.py verify form.md chinese_score

# 归纳规则
python $AS/src/cli.py induce satisfaction survey1.md survey2.md survey3.md

# 查看帮助
python $AS/src/cli.py --help
python $AS/src/cli.py fill --help
```
