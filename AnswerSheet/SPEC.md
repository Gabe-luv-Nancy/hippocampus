# AnswerSheet 格式规范

> 版本: 1.0.0  
> 状态: 草案  
> 日期: 2026-05-12

---

## 1. 概述

AnswerSheet 是一种**纯明文可验证填表格式**，以 Markdown 文件为载体。其核心设计目标：

- **人可读**：任何文本编辑器均可直接查看和编辑
- **可验证**：填入的内容可以通过密码学或逻辑归纳手段进行校验
- **角色分离**：通过 module 机制区分不同角色的填写权限
- **零依赖**：只需要一个标准的 Markdown 文件

### 1.1 核心机制

1. **YAML front matter** 声明 modules（权限角色）和全局元数据
2. **正文** 使用 `{{ slot:name | ... }}` 语法声明填空位置
3. **有监督模式 (supervised)**：创建者在文件底部存放加密/hashed answer，fill-in 对比验证
4. **无监督模式 (induction)**：通过归纳规则（从已验证实例归纳模式）验证

---

## 2. 文件结构

一个 AnswerSheet 文件由三部分组成：

```
┌─────────────────────────────┐
│  YAML Front Matter          │  ← 元数据、模块定义
├─────────────────────────────┤
│  Markdown 正文              │  ← 包含 slot 声明的正文
├─────────────────────────────┤
│  答案区（可选）              │  <!-- answers --> 之后
└─────────────────────────────┘
```

---

## 3. YAML Front Matter

位于文件开头，以 `---` 分隔。

### 3.1 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `answersheet` | string | 固定值 `"1.0"`，标识此文件为 AnswerSheet 格式 |
| `title` | string | 文件标题 |
| `modules` | list[object] | 权限角色列表 |

### 3.2 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 文件描述 |
| `version` | string | 文件版本号 |
| `created` | string | 创建日期（ISO 8601） |
| `author` | string | 作者 |

### 3.3 module 定义

每个 module 是一个对象，包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 模块名称，唯一标识 |
| `role` | string | ✅ | 角色描述（如 `creator`, `filler`, `reviewer`） |
| `description` | string | ❌ | 模块说明 |

**示例：**

```yaml
---
answersheet: "1.0"
title: "学生考试成绩单"
modules:
  - name: teacher
    role: creator
    description: "出卷教师，负责创建答案"
  - name: student
    role: filler
    description: "答题学生，负责填写答案"
  - name: admin
    role: reviewer
    description: "管理员，负责审核"
---
```

---

## 4. Slot 语法

Slot（填空位）是 AnswerSheet 的核心概念。在 Markdown 正文中，以特殊标记声明。

### 4.1 基本语法

```
{{ slot:<名称> | module=<模块名> [, verify=<验证模式>] [, rule=<规则>] }}
```

### 4.2 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `slot:<名称>` | ✅ | slot 的唯一标识符，名称只能包含字母、数字、下划线 |
| `module` | ✅ | 有权填写此 slot 的 module 名称 |
| `verify` | ❌ | 验证模式：`supervised`（有监督）或 `induction`（无监督归纳），默认 `supervised` |
| `rule` | ❌ | 验证规则，格式取决于验证模式 |

### 4.3 已填充的 Slot

当 slot 被填写后，格式变为：

```
{{ slot:<名称> | module=<模块名> | value=<填写值> }}
```

### 4.4 Slot 示例

**未填充：**

```markdown
姓名：{{ slot:name | module=student }}

班级：{{ slot:class | module=admin, verify=induction, rule=pattern:"^[甲乙丙]班$" }}

成绩：{{ slot:score | module=teacher, verify=supervised, rule=range:0-100 }}
```

**已填充：**

```markdown
姓名：{{ slot:name | module=student | value=张三 }}

班级：{{ slot:class | module=admin, verify=induction, rule=pattern:"^[甲乙丙]班$" | value=甲班 }}

成绩：{{ slot:score | module=teacher, verify=supervised, rule=range:0-100 | value=95 }}
```

---

## 5. 验证模式

### 5.1 有监督模式 (supervised)

**原理**：创建者在文件底部的答案区预先存放答案的哈希值或加密值。填写后，系统对比填写值与预存答案。

**答案区格式**：

答案区以 HTML 注释 `<!-- answers -->` 开始，之后每一行格式为：

```
[slot名称]: <验证数据>
```

**验证数据类型**：

| 类型 | 格式 | 说明 |
|------|------|------|
| `sha256` | `sha256:<hex>` | 对填写值直接做 SHA-256 |
| `md5` | `md5:<hex>` | 对填写值直接做 MD5 |
| `plain` | `plain:<明文>` | 明文存储（仅用于测试） |

**示例答案区**：

```markdown
<!-- answers -->
[name]: sha256:a1b2c3d4e5f6...
[score]: sha256:f6e5d4c3b2a1...
[comment]: plain:做得不错
```

**验证流程**：

1. 解析 front matter，识别所有 slot
2. 解析答案区，提取预存验证数据
3. 对每个 `verify=supervised` 的 slot：
   a. 读取填写值
   b. 用相同算法计算哈希
   c. 比较计算值与预存值
4. 所有匹配则验证通过

### 5.2 无监督模式 (induction)

**原理**：没有预存答案。通过从多个已验证实例中归纳出模式规则，用归纳出的规则验证新实例。

**规则类型**：

| 类型 | 格式 | 说明 |
|------|------|------|
| `pattern` | `pattern:"<regex>"` | 正则表达式匹配 |
| `range` | `range:<min>-<max>` | 数值范围 |
| `enum` | `enum:<v1>,<v2>,...` | 枚举值 |
| `length` | `length:<min>-<max>` | 字符串长度范围 |

**归纳流程**：

1. 收集多个已通过验证的实例（作为训练集）
2. 对每个 induction slot：
   - 收集所有已验证的填写值
   - 尝试归纳出规则（如正则模式、数值范围、枚举值）
3. 用归纳出的规则验证新的填写值

---

## 6. 完整文件示例

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

## 基本信息

学生姓名：{{ slot:student_name | module=student }}
学号：{{ slot:student_id | module=student }}

## 考试成绩

语文：{{ slot:chinese_score | module=teacher, verify=supervised }}
数学：{{ slot:math_score | module=teacher, verify=supervised }}

## 教师评语

{{ slot:comment | module=teacher, verify=induction, rule=pattern:"^.{10,200}$" }}

<!-- answers -->
[chinese_score]: sha256:5d41402abc4b2a76b9719d911017c592
[math_score]: sha256:7d793037a0760186574b0282f2f435e7
```

---

## 7. 错误码

| 错误码 | 含义 |
|--------|------|
| `E001` | front matter 格式错误 |
| `E002` | 缺少必填字段 |
| `E003` | slot 语法错误 |
| `E004` | module 未定义 |
| `E005` | 验证失败（哈希不匹配） |
| `E006` | 归纳验证失败（不匹配规则） |
| `E007` | 答案区格式错误 |
| `E008` | slot 未填写 |
| `E009` | 重复的 slot 名称 |

---

## 8. 设计理念

1. **纯明文优先**：所有数据以可读文本存储，不依赖二进制格式
2. **最小惊讶**：语法尽量贴近已有的模板语言（如 Jinja2、Mustache）
3. **渐进增强**：简单场景只需 module 和 slot，复杂场景可加 verify 和 rule
4. **离线可用**：不依赖网络或外部服务即可完成全部验证

---

## 附录 A：EBNF 语法参考

```
file         = front_matter body [answer_section]
front_matter = "---" yaml_content "---"
body         = { (text | slot) }
slot         = "{{" "slot:" name params "}}"
params       = { "|" param }
param        = key "=" value
answer_section = "<!-- answers -->" { answer_line }
answer_line  = "[" name "]:" ":" hash_type ":" hash_value
```
