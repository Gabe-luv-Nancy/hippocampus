# HIPPO — Task Schema System

> Schema-core for HIPPO V4. Manages structured task registry with YAML backend and zero-external-dependency validation.

## 核心理念

Schema 是 HIPPO V4 的**核心创新**——AI 任务进度表，让 AI 照章办事、无法赖账。

```
AI: "我要把任务 HIPPO-XXX 标记为 done"
        ↓
validator.py: "你的 file_refs 全部 verified=true 了吗？"
        ↓
AI: 逐个文件路径验证 → 只有文件真实存在才能写入 done
        ↓
写不进去就是写不进去，AI 无可争辩
```

---

## 文件结构

```
scripts/task_schema/
├── schema_models.py   # 数据模型（TaskSchema / FileRef）
├── validator.py       # 规则引擎（按规则才能写入）
├── registry.py        # YAML 读写接口
├── registry.yaml      # 任务总表（ED 管理，Programmer 不可直接修改）
└── README.md          # 本文件
```

---

## 快速开始

```python
import sys
sys.path.insert(0, "scripts/task_schema")

from schema_models import TaskSchema, FileRef
from registry import load_registry, save_registry, get_task, list_tasks

# 加载所有任务
registry_path = "scripts/task_schema/registry.yaml"
all_tasks = load_registry(registry_path)
print(f"Loaded {len(all_tasks)} tasks")

# 按状态查询
in_progress = list_tasks(registry_path, status="in_progress")

# 获取单个任务
task = get_task("HIPPO-20260420-002", registry_path)
print(task.title, task.status)
```

---

## 数据模型

### FileRef

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | `str` | 文件真实路径（POSIX 格式） |
| `verified` | `bool` | `True` = 文件存在已确认 |

### TaskSchema

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `str` | ✅ | 格式：`HIPPO-YYYYMMDD-NNN` |
| `title` | `str` | ✅ | 任务标题，≤100 字 |
| `status` | `str` | ✅ | `proposed`/`approved`/`in_progress`/`done` |
| `assignee` | `str` | ✅ | `ran`/`fep`/`bes`/`ed` |
| `phase` | `str` | ✅ | `v4.1`/`v4.2`/`v4.3` |
| `file_refs` | `list[FileRef]` | ❌ | 需验证的文件引用列表 |
| `depends_on` | `list[str]` | ❌ | 依赖的其他任务 ID |

---

## 验证规则

```python
from validator import validate_task

errors = validate_task(task)
if errors:
    print("Validation failed:", errors)
```

**强制规则：**

| 场景 | 合法？ | 原因 |
|------|--------|------|
| `status="proposed"`，无 `file_refs` | ✅ | 无需验证 |
| `status="done"`，所有 `file_refs[].verified=true` | ✅ | 文件全部确认 |
| `status="done"`，部分 `file_refs[].verified=false` | ❌ | 存在未验证文件 |
| `verified=true` 但文件不存在 | ❌ | 文件未找到 |
| 无效的 `id` 格式 | ❌ | 必须符合 `HIPPO-YYYYMMDD-NNN` |
| 无效的 `status`/`assignee`/`phase` | ❌ | 必须在合法集合内 |

---

## 核心操作

```python
from registry import (
    load_registry, save_registry,
    add_task, update_task,
    get_task, list_tasks,
    validate_all,
)

registry_path = "scripts/task_schema/registry.yaml"

# 加载 / 保存
tasks = load_registry(registry_path)
save_registry(tasks, registry_path)

# 添加新任务
new_task = TaskSchema(
    id="HIPPO-20260422-001",
    title="Example task",
    status="proposed",
    assignee="bes",
    phase="v4.1",
    file_refs=[],
    depends_on=[],
)
add_task(new_task, registry_path)

# 更新任务
updated = update_task("HIPPO-20260422-001", registry_path, status="in_progress")

# 查询
task = get_task("HIPPO-20260420-001", registry_path)
pending = list_tasks(registry_path, status="pending")

# 验证所有任务
report = validate_all(registry_path)
if report:
    print("Errors found:", report)
else:
    print("All tasks valid ✓")
```

---

## YAML Registry 格式

```yaml
# HIPPO V4 Task Registry
tasks:
  - id: HIPPO-20260420-001
    title: 双版本自检
    status: done
    assignee: ran
    phase: v4.1
    file_refs:
      - path: /mnt/x/CLABIN/HIPPO/hippocampus-for-clawhub/PROMPT.md
        verified: true
    depends_on: []
```

---

## 技术约束

- **零外部依赖** — 仅用标准库（`dataclasses`、`pathlib`、`re`、`yaml`）
- 路径全部 **POSIX 兼容**（无 Windows 反斜杠）
- YAML 输出人类可读、人类可编辑
- `registry.yaml` 由 ED 统一管理，Programmer 不直接修改

---

## 迭代日志

### v4.1 — Schema Core（2026-04-22）

**首次实现**

- `schema_models.py`（68行）：`TaskSchema` / `FileRef` 数据类定义
- `validator.py`（73行）：强制打钩规则引擎，`status=done` 必须 file_refs 全部 verified
- `registry.py`（115行）：YAML 读写接口，`load_registry`/`save_registry`/`add_task`/`update_task`/`list_tasks`/`validate_all`
- `registry.yaml`：任务总表，包含 HIPPO-20260420-001 ~ 004 四个任务
- `README.md`：模块说明文档
- **技术创新：YAML-based registry，无外部依赖，标准库实现**

### v4.2（待开发）

- Auto-Extract 模块

### v4.3（待开发）

- 集成测试 + 完整文档

---

*本文档随 HIPPO Schema 模块同步更新*
