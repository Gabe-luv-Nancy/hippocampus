# AnswerSheet 可验证填表机制 — 市场/技术调研报告

> 调研时间：2026-05-12
> 调研目标：评估鱼总提出的「AnswerSheet」纯明文可验证填表格式的创新性与市场空白

---

## 一、AnswerSheet 概念速览

| 特征 | 描述 |
|------|------|
| **载体** | 纯明文文件（非数据库、非Web系统） |
| **Module权限声明** | 文件头部声明哪些模块/角色的用户才有权修改 |
| **条件化 fill-in** | 每个填空处声明前置条件，满足条件才能填写 |
| **有监督模式** | 创建者已知 answer（标准答案），填入值必须与 answer 对比通过才能 commit |
| **无监督模式** | 创建者 answer=null，通过 induction（归纳推理）规则验证填入值的正确性 |
| **最终产物** | 明文表单文件本身，非配置系统、非软件系统 |

---

## 二、现有方案全面梳理

### 2.1 开源项目/工具

| # | 项目 | 星标 | 与 AnswerSheet 的关系 | 关键差异 |
|---|------|------|----------------------|----------|
| 1 | **MarkdownForms** (Dispatch-Dataworks) | ★1 | **最近似项目** — 纯 Markdown 的可填写表单格式规范，支持空白、勾选、下拉等表单控件，有内联验证元数据 | ❌ 无权限控制、无有监督/无监督双模式、无 induction 验证 |
| 2 | **W3C Verifiable Credentials (did-jwt-vc)** | ★208 | 可验证凭证标准，JWT 格式签发/验证身份凭证 | ❌ 面向身份验证而非表单填写；需加密基础设施；非纯明文 |
| 3 | **Dhall Language** | ★4444 | 可维护的配置语言，类型安全的纯文本配置 | ❌ 面向配置文件而非表单范式；无权限/验证模式概念 |
| 4 | **JSON Schema** (json-schema-org) | — | 声明式数据验证标准 | ❌ 无权限控制、无填空语义、无有监督/无监督模式 |
| 5 | **XForms (W3C/OASIS)** | — | XML 表单标准，支持条件化字段、计算、验证 | ❌ 基于 XML 而非明文；重量级标准；无有监督/无监督双模式 |
| 6 | **OPA (Open Policy Agent) + Rego** | ★9500+ | 策略即代码，声明式策略验证 | ❌ 通用策略引擎，非表单格式；需运行时 |
| 7 | **Repeatr (polydawn)** | ★68 | 内容寻址的可复现计算，JSON API | 仅借鉴了内容寻址概念，与表单范式无直接关系 |
| 8 | **CryptPad** | ★3000+ | 加密协作平台，含表单功能 | ❌ 是 Web 平台而非纯文本格式 |
| 9 | **OMR Scanner 系列** | 多个 | 光学阅卷/答题卡扫描系统 | ❌ 面向纸质 OMR 识别，非纯文本格式范式 |

### 2.2 学术/理论概念

| # | 概念 | 来源 | 与 AnswerSheet 的关系 | 关键差异 |
|---|------|------|----------------------|----------|
| 1 | **Proof-Carrying Data (PCD)** | Alessandro Chiesa 等 (2012-) | 数据本身携带正确性证明，可在链条中逐跳验证 | 学术框架，需 ZK 密码学；AnswerSheet 更轻量，用明文+规则替代密码学证明 |
| 2 | **Proof-Carrying Code (PCC)** | George Necula (1997) | 代码附带形式化证明，验证方可检查安全性 | 面向代码安全而非表单填写 |
| 3 | **Verified Computation** | 多个 (ZK rollup 等) | 可验证计算——验证者可检查计算正确性 | Constantine (★488)、Fusion (★118) 等项目均在 ZK 层面；远超"纯明文"的轻量化目标 |
| 4 | **Literate Programming** | Donald Knuth (1984) | 文档与代码交织，文档即程序 | 概念层面类似（文档即功能），但面向编程而非填表 |
| 5 | **Executable Documents** | Jupyter, Org-mode, R Markdown | 文档内嵌可执行代码 | ❌ 需要运行时环境；非权限控制+验证范式 |
| 6 | **Content-Addressable Storage** | IPFS, Git,Repeatr | 用内容哈希寻址和验证数据完整性 | 仅提供"不可篡改"属性，不解决"谁有权填+填得对不对"问题 |
| 7 | **Inductive Verification** | Coq, Lean, Isabelle | 归纳法证明数据/命题的正确性 | 重型定理证明器；AnswerSheet 借鉴"induction"概念但用轻量规则替代完整证明 |
| 8 | **JSON Schema Validation** | IETF Draft | 声明式数据约束验证 | 最接近的工业标准，但缺乏权限、双模式验证、induction |
| 9 | **CDDL (RFC 8610)** | IETF | CBOR 数据定义语言，纯文本描述数据结构 | 面向二进制数据(CBOR)的 schema，无填空/权限概念 |

### 2.3 GitHub 关键词搜索矩阵

| 搜索关键词 | 有意义结果 | 说明 |
|-----------|----------|------|
| `verifiable form validation` | 无直接相关 | 返回 W3C 文档、白皮书等杂项 |
| `answer sheet verification` | OMR 扫描类 | 全部是光学阅卷，非文本格式 |
| `content addressable form` | 无直接相关 | 返回杂项 |
| `plain text form schema validation` | MarkdownForms (★1) | 唯一直接相关项目 |
| `executable document plain text` | 无直接相关 | |
| `prolog verification form rules` | 无结果 | |
| `zero knowledge document verification` | 无直接相关 | |
| `induction rule verification document` | 无结果 | |
| `answer sheet format specification` | 无结果 | |
| `fill in the blank verification format` | 无结果 | |
| `proof carrying data` | arkworks-rs/pcd (★37) 等 | ZK 密码学框架 |

---

## 三、对比分析：AnswerSheet 的创新点

### 3.1 创新度评估矩阵

```
                        现有方案覆盖程度
                        ○ = 无  △ = 部分覆盖  ● = 充分覆盖

+---------------------------+------+------+------+---------+-----------+
| 核心特征                   | JSON | XForms | VC/JWT | Markdown | AnswerSheet |
|                           |Schema| (W3C) | (W3C) | Forms   | (鱼总方案) |
+---------------------------+------+------+------+---------+-----------+
| 纯明文载体                 |  △   |  ○   |  ○   |   ●     |    ●      |
| Module权限声明             |  ○   |  △   |  △   |   ○     |    ●      |
| 条件化 fill-in             |  △   |  ●   |  ○   |   △     |    ●      |
| 有监督验证(answer对比)     |  ○   |  ○   |  △   |   ○     |    ●      |
| 无监督验证(induction)      |  ○   |  ○   |  ○   |   ○     |    ●      |
| 零依赖(无运行时)           |  ●   |  ○   |  ○   |   ○     |    ●      |
| 表单范式(非配置/非系统)    |  ○   |  ●   |  ○   |   ●     |    ●      |
+---------------------------+------+------+------+---------+-----------+
```

### 3.2 核心创新点（3个独到之处）

#### 🔥 创新点 1：有监督/无监督双模式验证架构

**没有任何现有方案同时支持这两种模式：**
- **有监督模式**（answer ≠ null）：类似于"考试答题"——出题者知道标准答案，答题者填入后对比验证
- **无监督模式**（answer = null）：类似于"开放性研究"——出题者不知道答案，但通过 induction 规则（归纳推理：从已有正确实例归纳出验证模式）来验证

最接近的类比是 Kaggle 的 private leaderboard（有监督），但不存在"无监督验证"的对等物。W3C VC 可以验证凭证真实性，但不验证填入内容正确性。XForms 有条件验证但没有"验证模式"概念。

#### 🔥 创新点 2：Module 权限声明 + 条件化 fill-in 的明文融合

在纯明文文件中将**权限声明**（谁有权填）和**条件声明**（什么条件下可填）统一在同一个文件头/字段中，无需外部策略引擎（如 OPA）或外部身份系统（如 W3C DID）。

XForms 虽然有条件化字段（`relevant`、`required`），但：
1. 它是 XML 格式，非"纯明文"
2. 权限控制依赖外部系统
3. 没有验证模式概念

#### 🔥 创新点 3：Induction 验证机制

这是最具原创性的点。现有验证框架（JSON Schema、CDDL、TLA+、Coq/Lean）都是**演绎式**的——预设规则，检查数据是否满足规则。

AnswerSheet 的 induction 验证是**归纳式**的——创建者不知道答案，但系统通过已通过验证的实例集合归纳出正确性模式（类似于机器学习中的 few-shot learning 或类型推断中的 Hindley-Milner 推导）。

**在表单/文档验证领域，没有任何开源项目或学术框架实现了这种"归纳式验证"的纯文本范式。**

### 3.3 非创新点（已有先例的部分）

| 特征 | 先例 |
|------|------|
| 纯明文表单格式 | MarkdownForms、Dhall、TOML/YAML 配置 |
| 声明式字段验证 | JSON Schema、CDDL、XForms |
| 内容完整性验证 | Git (SHA1)、IPFS (CID)、Content-Addressable 存储 |
| 角色权限控制 | RBAC (NIST)、OPA/Rego、XACML |

---

## 四、推荐实现路径

### 4.1 格式设计建议

```
推荐使用 Markdown + YAML front matter 作为载体：

---
# AnswerSheet Meta
version: answersheet/0.1
modules:
  - name: admin
    permission: [create, read, fill, verify]
  - name: reviewer  
    permission: [read, fill, verify]
  - name: applicant
    permission: [read, fill]
---

# 项目申请表

## 基本信息

- 项目名称: {{ slot:name | required:true | module:applicant }}
- 申请金额: {{ slot:amount | type:number | min:1000 | module:applicant | verify:induction }}

## 审批

- 审批意见: {{ slot:comment | module:reviewer | verify:supervised | answer:[hidden] }}
- 批准金额: {{ slot:approved_amount | module:admin | verify:induction | rule:lte(slot:amount) }}
```

### 4.2 分阶段实现路线

```
Phase 1: 格式规范 (1-2周)
├── 定义 AnswerSheet 文件格式 EBNF
├── 定义 Module 权限声明语法
├── 定义 slot（填空）语法
└── 定义验证模式标记 (supervised / induction)

Phase 2: 核心验证引擎 (2-4周)
├── 有监督验证器（answer 对比）
├── Induction 验证器
│   ├── 基于规则的归纳（类型推断、约束传播）
│   └── 基于统计的归纳（k-NN、模式匹配）
└── 权限检查器（Module ACL）

Phase 3: 工具链 (2-4周)
├── answersheet CLI（验证、填表、diff）
├── answersheet parser（多语言 SDK）
├── Git hook 集成（commit 前自动验证）
└── GitHub Action（PR 自动验证填表）

Phase 4: 生态 (持续)
├── VS Code 插件（语法高亮+智能提示）
├── 模板市场
└── 与 W3C VC 的桥接（可选）
```

### 4.3 Induction 验证的技术选型

| 方案 | 复杂度 | 效果 | 推荐度 |
|------|--------|------|--------|
| **规则引擎**（内置约束表达式） | 低 | 中 | ⭐⭐⭐⭐⭐ Phase 1 首选 |
| **类型推断**（Hindley-Milner 式） | 中 | 高 | ⭐⭐⭐⭐ Phase 2 进阶 |
| **统计归纳**（基于已验证实例集） | 中高 | 高 | ⭐⭐⭐ Phase 3 可选 |
| **ZK 证明**（arkworks PCD 等） | 极高 | 极高 | ⭐ 远期可选 |

**推荐：Phase 1 用简单的约束表达式实现 induction（如 `rule:lte(slot:amount)`, `rule:regex("[A-Z]+")`, `rule:consistent_with(field:x)`），后续迭代中加入类型推断和统计归纳。**

### 4.4 生态对标与差异化定位

```
轻量化谱系：

重 ←————————————————————————————→ 轻

  Coq/Lean    TLA+    XForms    JSON Schema    Dhall    MarkdownForms    ★AnswerSheet★
  (定理证明)  (规范)  (XML表单)  (数据验证)    (配置)    (MD表单)        (可验证明文表单)
  
  ✗ 不需要运行时                                                              ✓ 纯文本
  ✗ 无权限控制                                                                ✓ Module ACL
  ✗ 无双模式验证                                                              ✓ supervised + induction
```

---

## 五、结论

### AnswerSheet 的市场定位

**存在明确的市场空白。** 没有任何现有项目/标准同时满足以下全部条件：
1. ✅ 纯明文文件格式
2. ✅ 内建 Module 权限声明
3. ✅ 条件化 fill-in
4. ✅ 有监督验证（answer 对比）
5. ✅ 无监督验证（induction 归纳）

最接近的竞品是 **MarkdownForms**（★1，仅 2026-01 创建），但它只解决了"纯明文表单"部分，完全没有权限、双模式验证和 induction 概念。

### 创新性判断

| 维度 | 评级 | 说明 |
|------|------|------|
| **整体创新性** | ⭐⭐⭐⭐ 高 | 5 个核心特征的组合是空白的 |
| **单个特征** | ⭐⭐⭐ 中 | 每个特征单独看都有先例（JSON Schema、RBAC、PCD等） |
| **Induction 验证** | ⭐⭐⭐⭐⭐ 极高 | 在表单/文档验证领域的归纳式验证，无直接先例 |
| **实用价值** | ⭐⭐⭐⭐ 高 | 填补了"重系统"和"无验证"之间的巨大空白 |
| **可实施性** | ⭐⭐⭐⭐ 高 | 纯文本格式，低技术门槛，Phase 1 可快速出 MVP |

### 风险提示

1. **格式碎片化风险** — 明文格式易衍生不兼容版本，建议早期定义严格的 EBNF 规范
2. **Induction 的可靠性** — 归纳验证可能出现假阳性/假阴性，建议明确其适用场景边界
3. **与现有标准的互补性** — 建议明确与 JSON Schema、W3C VC 的互补关系而非竞争关系

---

*报告完成。AnswerSheet 概念具有明确的创新性，尤其是 induction 验证模式和双模式架构在纯文本表单领域属于首创。建议以 Markdown + YAML front matter 为载体快速落地 MVP。*
