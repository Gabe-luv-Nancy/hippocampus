# Hippocampus v3.2 开发流程记录

> 本文档记录 GitHub 版本的完整开发过程
> 用于生成 Clawhub 提示词注入版本

---

## 开发环境

- **开发路径**: `/root/clabin_sync/HIPPO/github-workspace/hippocampus/`
- **最终路径**: `hippocampus/hippocampus-for-github/`
- **Python 版本**: 3.8+

---

## 文件清单

### 核心脚本

| 文件 | 用途 | 行数 |
|------|------|------|
| `scripts/memory.py` | 核心记忆引擎（从 v3.0 继承） | ~650 |
| `scripts/capture.py` | AI 记忆抓取模块（新增） | ~450 |
| `scripts/analyzer.py` | 本地分析模块（新增） | ~500 |
| `scripts/usb_manager.py` | U盘管理模块（新增） | ~400 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `capture/openclaw.yaml` | OpenClaw 路径配置 |
| `capture/doubao.yaml` | 豆包路径配置 |

### U盘产品

| 文件 | 用途 |
|------|------|
| `U/autorun.bat` | Windows 自动运行 |
| `U/autorun.sh` | macOS/Linux 自动运行 |
| `U/HIPPOCAMPUS_Marker.txt` | 产品标识文件 |

### 文档

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 技能定义 |
| `skill.yaml` | 元数据 |
| `USER_CONFIG.md` | 用户配置 |
| `VERSION` | 版本号 |
| `README.md` | 项目入口 |
| `CHANGELOG.md` | 变更记录 |

### Clawhub 版本

| 文件 | 用途 |
|------|------|
| `hippocampus-for-clawhub/PROMPT.md` | 安装提示词 |
| `hippocampus-for-clawhub/CLAWHUB.yaml` | Clawhub metadata |

---

## 开发步骤

### Step 1: 创建目录结构

```bash
mkdir -p /root/clabin_sync/HIPPO/github-workspace/hippocampus/hippocampus-for-github/{scripts,frontend/{static,templates},capture,U/{model,capture,db,output},docs}
mkdir -p /root/clabin_sync/HIPPO/github-workspace/hippocampus/hippocampus-for-clawhub
mkdir -p /root/clabin_sync/HIPPO/github-workspace/hippocampus/.github/workflows
```

### Step 2: 编写 capture.py

**关键类**: `CaptureEngine`

```python
class CaptureEngine:
    def __init__(self, output_dir: str, config_file: str = None)
    def capture_single(self, ai_type: str, force: bool = False) -> Dict
    def capture_all(self, force: bool = False) -> Dict
    def generate_manifest(self) -> str
```

**关键类**: `PathScanner`

```python
class PathScanner:
    @staticmethod
    def scan_common_locations() -> Dict[str, List[str]]
    @staticmethod
    def detect_ai_types() -> List[Dict[str, str]]
```

### Step 3: 编写 analyzer.py

**关键类**: `SimpleVectorDB`

```python
class SimpleVectorDB:
    def __init__(self, db_path: str)
    def add_document(self, doc_id: str, source: str, content: str, file_path: str = None)
    def search(self, query: str, limit: int = 10, sources: List[str] = None) -> List[Dict]
```

**关键类**: `Analyzer`

```python
class Analyzer:
    def __init__(self, base_dir: str = ".")
    def index_captured_files(self) -> Dict[str, Any]
    def query(self, query: str, sources: List[str] = None) -> List[Dict]
    def generate_summary(self) -> Dict[str, Any]
    def export_report(self, format: str = "json") -> str
```

### Step 4: 编写 usb_manager.py

**关键类**: `USBAutoRunner`

```python
class USBAutoRunner:
    def __init__(self, usb_root: str)
    def log(self, message: str)
    def run_capture(self) -> Dict
    def run_analyze(self) -> Dict
    def run_full_cycle(self) -> Dict
```

**关键类**: `OpenClawBridge`

```python
class OpenClawBridge:
    def __init__(self, usb_root: str, host_config: Dict = None)
    def write_request(self, request_type: str, data: Dict) -> str
    def read_response(self, timeout: int = 60) -> Optional[Dict]
    def exchange(self, request_type: str, data: Dict, timeout: int = 60) -> Optional[Dict]
```

### Step 5: 编写 U 盘 autorun

**Windows** (`U/autorun.bat`):
- 检测 U 盘盘符
- 检查 Hippocampus 标识
- 依次运行 capture.py 和 analyzer.py
- 打开 output 目录

**macOS/Linux** (`U/autorun.sh`):
- 检测 U 盘挂载点
- 同样流程

### Step 6: 编写 capture 配置

每个 AI 类型一个 YAML 文件，包含：
- `name`: 显示名称
- `paths`: 抓取路径列表（支持通配符）
- `priority`: 优先级
- `enabled`: 是否启用

### Step 7: 编写 PROMPT.md

Clawhub 提示词的结构：
1. 执行步骤概览
2. 每个文件的详细生成指令
3. 验证方法
4. 版本信息

---

## 依赖关系

```
memory.py (核心)
    ↓
    ├─ capture.py (抓取 → 存储到 chronicle)
    │       ↓
    │       capture/*.yaml (AI 路径配置)
    │
    └─ analyzer.py (从 capture 读取 → 分析 → 报告)
            ↓
            usb_manager.py (USB 产品交互)
```

---

## 部署流程

### GitHub 版本发布

```bash
# 1. 提交所有更改
cd /root/clabin_sync/HIPPO/github-workspace/hippocampus
git add .
git commit -m "v3.2.0: Add capture, analyzer, USB support"

# 2. 创建 tag
git tag v3.2.0
git push origin master --tags

# 3. GitHub Actions 自动发布
```

### Clawhub 版本发布

```bash
# 1. 从 GitHub 版本提取代码
# 2. 更新 PROMPT.md 中的代码片段
# 3. 上传到 Clawhub
```

---

## 测试清单

- [x] `python3 capture.py --list` 列出支持的 AI
- [x] `python3 capture.py --scan` 扫描系统中已安装的 AI
- [x] `python3 capture.py -o ./capture` 抓取记忆
- [x] `python3 analyzer.py -b . -i` 索引文件
- [x] `python3 analyzer.py -b . -q "关键词"` 查询
- [x] `python3 analyzer.py -b . -r markdown` 生成报告
- [x] `python3 memory.py init` 初始化数据库
- [x] `python3 memory.py status` 查看状态
- [x] USB autorun 在 Windows 上运行
- [x] USB autorun 在 macOS 上运行

---

## 版本信息

- **当前版本**: 3.2.0
- **发布日期**: 2026-04-05
- **下一个版本**: 3.3.0 (规划中)
