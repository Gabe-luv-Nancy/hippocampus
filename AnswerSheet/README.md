# AnswerSheet — 可验证填表明文范式

> **Verifiable Form-Filling Plaintext Paradigm**
> 一种极致轻量化的纯明文文件格式，支持角色权限声明、条件化填空、有监督/无监督双模式验证。

---

## 一句话理解

AnswerSheet 是一个 `.md` 文件。你往里面填内容，它能**自动验证你填得对不对**——用哈希对比、正则匹配、范围检查、枚举约束。

不需要数据库，不需要后端，不需要安装任何东西。一个 Markdown 文件就是一切。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| 📄 **纯明文** | 以 Markdown 文件为载体，任何编辑器都能打开 |
| 🔒 **角色权限** | 通过 module 机制区分创建者、填写者、审核者 |
| ✅ **双模式验证** | 有监督（哈希对比标准答案）+ 无监督（归纳规则约束） |
| 🧠 **归纳引擎** | 从多份已填表自动归纳出验证规则 |
| ⚡ **零依赖** | 纯 Python，只需要 PyYAML |
| 📐 **格式规范** | 完整 SPEC.md 含 EBNF 语法定义 |

---

## 快速理解：一个文件长什么样

```markdown
---
answersheet: "1.0"
title: "学生考试成绩单"
modules:
  - name: teacher
    role: creator
  - name: student
    role: filler
created: "2026-05-12"
---

# 学生考试成绩单

## 基本信息（学生填写）
姓名：{{ slot:student_name | module=student }}
学号：{{ slot:student_id | module=student }}

## 考试成绩（教师填写，有监督验证）
语文：{{ slot:chinese | module=teacher, verify=supervised }}
数学：{{ slot:math | module=teacher, verify=supervised }}

## 教师评语（归纳验证，10-200字）
{{ slot:comment | module=teacher, verify=induction, rule=pattern:"^.{10,200}$" }}

<!-- answers -->
[chinese]: sha256:a3f7b2c1d4e5...
[math]: sha256:7d793037a076...
```

**关键概念一目了然：**
- `modules` → 谁有权限操作
- `{{ slot:xxx | module=yyy }}` → 谁填这个空
- `verify=supervised` → 底部有标准答案，哈希对比
- `verify=induction` → 用规则（正则/范围/枚举）约束
- `<!-- answers -->` → 标准答案区（仅 supervised 模式）

---

## 文件结构

```
AnswerSheet/
├── README.md          ← 你在这里
├── SPEC.md            ← 格式规范 v1.0（含 EBNF 语法）
├── SKILL.md           ← Agent/Skill 集成说明
├── RESEARCH.md        ← 市场/技术调研报告（20+ 竞品分析）
├── src/
│   ├── __init__.py    ← Python 包入口
│   ├── answersheet.py ← 核心引擎（Parser + Validator + Filler + InductionEngine）
│   └── cli.py         ← 命令行工具（5 个子命令）
├── examples/
│   ├── sample-supervised.md  ← 有监督模式示例（考试卷）
│   └── sample-induction.md   ← 无监督模式示例（产品调研）
└── tests/
    └── test_core.py   ← 23 个单元测试（全通过 ✅）
```

---

## 安装

```bash
git clone https://github.com/Gabe-luv-Nancy/answersheet.git
cd answersheet
pip install pyyaml   # 唯一外部依赖
```

没有 `setup.py`，没有 `pyproject.toml`——这是有意为之。AnswerSheet 的哲学是**零包装、零复杂度**。直接 `import` 就能用。

---

## 使用方法

### CLI 命令行

```bash
cd src

# 查看表单结构
python cli.py info ../examples/sample-supervised.md

# 填写一个 slot
python cli.py fill form.md -s student_name -v "张三"

# 全文验证
python cli.py validate form.md

# 验证单个 slot
python cli.py verify form.md chinese

# 从多份表归纳规则
python cli.py induce satisfaction survey1.md survey2.md survey3.md
```

### Python API

```python
import sys
sys.path.insert(0, 'src')

from answersheet import (
    AnswerSheetParser, AnswerSheetValidator,
    AnswerSheetFiller, InductionEngine, parse_file
)

# 解析文件
sheet = parse_file("form.md")

# 查看结构
for slot in sheet.slots:
    print(f"{slot.name}: module={slot.module}, verify={slot.verify.value}")

# 填充
filler = AnswerSheetFiller()
content = filler.fill(content, "student_name", "张三")

# 验证
validator = AnswerSheetValidator()
result = validator.validate(sheet)
# → {"valid": True/False, "errors": [...], "warnings": [...]}

# 归纳规则
engine = InductionEngine()
rule = engine.induce(["92", "88", "95", "90"], rule_type="auto")
# → "range:88.0-95.0"
```

---

## 三种角色怎么用

### 🎓 创建者（Creator）

**职责**：设计表单结构、分配角色权限、设置验证规则、存放标准答案。

1. 在 Front Matter 里定义 `modules`（谁有权限）
2. 在正文里布置 `{{ slot:xxx }}` 填空位，绑定 module
3. 对需要验证的 slot 设置 `verify` 模式和 `rule`
4. 在 `<!-- answers -->` 区存放标准答案（哈希值）

```yaml
# 创建者控制权的体现：
modules:
  - name: teacher      # 只有 teacher 能填成绩
    role: creator
  - name: student      # 只有 student 能填姓名
    role: filler
```

### ✍️ 填写者（Filler）

**职责**：填写分配给自己 module 的 slot。

```bash
# 以 student 身份填写
python cli.py fill form.md -s student_name -v "张三"

# 以 teacher 身份填写
python cli.py fill form.md -s chinese -v "92"
```

填写者**只能操作绑定给自己 module 的 slot**。填别人的 slot 会在验证时报错。

### 🔍 审核者（Reviewer）

**职责**：验证填写结果的正确性。

```bash
# 全量验证
python cli.py validate form.md

# 以特定角色身份验证
python cli.py validate form.md -m student
```

---

## 两种验证模式

### 有监督模式（Supervised）

**场景**：你知道标准答案（如考试、测评）。

```
创建者预存答案哈希 → 填写者填入值 → 系统算哈希对比 → 匹配则通过
```

支持三种哈希：
- `sha256` — 生产环境，填写者无法反推答案
- `md5` — 轻量验证
- `plain` — 明文，仅测试用

### 无监督归纳模式（Induction）

**场景**：没有标准答案，但有规则约束（如调研、反馈）。

4 种规则：

| 规则 | 格式 | 例子 |
|------|------|------|
| 正则匹配 | `pattern:"<regex>"` | `pattern:"^\\d{4}-\\d{2}-\\d{2}$"` |
| 数值范围 | `range:<min>-<max>` | `range:0-100` |
| 枚举值 | `enum:<v1>,<v2>,...` | `enum:是,否,待定` |
| 长度范围 | `length:<min>-<max>` | `length:5-500` |

**归纳引擎**可以从多份已填表自动推断规则：

```python
InductionEngine().induce(["92", "88", "95", "90"], rule_type="auto")
# → "range:88.0-95.0"

InductionEngine().induce(["是", "否", "是", "待定"], rule_type="auto")
# → "enum:否,待定,是"
```

---

## 错误码

| 错误码 | 含义 |
|--------|------|
| E001 | front matter 格式错误 |
| E002 | 缺少必填字段 |
| E003 | slot 语法错误 |
| E004 | module 未定义 |
| E005 | 有监督验证失败（哈希不匹配） |
| E006 | 归纳验证失败（不匹配规则） |
| E007 | 答案区格式错误 |
| E008 | slot 未填写 |
| E009 | slot 名称重复 |

---

## 运行测试

```bash
cd answersheet
python -m pytest tests/test_core.py -v
# 23 passed ✅
```

---

## 创新性

详见 [RESEARCH.md](./RESEARCH.md)——调研了 20+ 组关键词、9 个开源项目、9 个学术概念后确认的 **3 个核心创新**：

1. 🔥 **有监督/无监督双模式验证架构** — 表单领域无先例
2. 🔥 **Module 权限 + 条件化 fill-in 的明文融合** — 无先例
3. 🔥 **Induction 归纳式验证** — 表单/文档领域首创

最近的竞品 MarkdownForms (★1) 仅支持基础表单渲染，不具备上述任何一项能力。

---

## 路线图

| 版本 | 内容 | 状态 |
|------|------|------|
| v1.0 | 核心引擎 + CLI + SPEC + 测试 + 调研 | ✅ 完成 |
| v1.1 | Ed25519 数字签名（密码学级权限强制执行） | 📋 规划中 |
| v1.2 | 多文件批量处理 + 统计报告 | 📋 规划中 |
| v2.0 | 可视化编辑器（Web UI） | 💡 概念阶段 |

### v1.1 签名机制预览

```
v1.0: {{ slot:score | module=teacher | value=95 }}
v1.1: {{ slot:score | module=teacher | value=95 | sig=ed25519:a3f7... }}
```

每个 module 持有 Ed25519 密钥对，填写时签名，验证时用公钥校验。实现密码学级别的权限强制执行，无需编译层或 OS 层介入。

---

## 设计哲学

1. **纯明文优先** — 所有数据以可读文本存储，不依赖二进制格式
2. **最小惊讶** — 语法贴近 Jinja2/Mustache 等模板语言
3. **渐进增强** — 简单场景只需 module 和 slot，复杂场景可加 verify 和 rule
4. **离线可用** — 不依赖网络或外部服务即可完成全部验证
5. **零包装** — 不需要 pip install，不需要 node_modules，import 即用

---

## License

MIT

---

*Created: 2026-05-12 | Concept by [Gabe](https://github.com/Gabe-luv-Nancy) | Engine by 赫墨 (Hermes Agent)*
