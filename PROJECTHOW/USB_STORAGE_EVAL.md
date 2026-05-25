# USB 存储空间需求评估报告

**项目**：HIPPO V4 USB 分发版存储需求  
**作者**：ran（ResearchAnalyst）  
**日期**：2026-04-22  
**状态**：初稿

---

## 一、当前 USB 版本代码库分析

### 1.1 基础数据（hippocampus-for-usb/）

| 指标 | 数值 |
|------|------|
| 总目录大小 | **118 MB** |
| 文件总数 | **32 个** |
| Python 代码行数 | **2,884 行**（7个 .py 文件） |
| 数据库文件 | `brain_dump.sqlite`（32 KB，当前为空库） |
| 静态资源 | UI 静态文件（HTML/JS/CSS）+ 2个图标 |

### 1.2 代码目录结构

```
hippocampus-for-usb/
├── SPEC.md                    # 规格说明（约 3 KB）
├── 构建说明.md                 # 构建说明（约 2 KB）
├── Hippocampus.exe           # PyQt6 编译后的 exe（约 60 MB，已打包）
├── brain_dump/
│   ├── *.bat                 # 启动脚本（5个）
│   ├── autorun.*             # 自动运行脚本（2个）
│   ├── marker.txt            # 产品标识
│   ├── README.md             # 说明文档
│   ├── 使用说明.md            # 使用指南
│   ├── server.py             # Web 后端（518 行）
│   ├── db/
│   │   ├── brain_dump.sqlite # SQLite 数据库（32 KB）
│   │   └── init_db.py        # 数据库初始化（209 行）
│   ├── lib/
│   │   ├── detector.py       # AI 工具检测（299 行）
│   │   ├── rules_engine.py   # 规则引擎（387 行）
│   │   ├── scanner.py        # 扫描器（495 行）
│   │   ├── streamlit_app.py  # Streamlit UI（612 行）
│   │   ├── usb_detector.py   # USB 检测（364 行）
│   │   └── config/
│   │       ├── ai_tools.yaml # AI 工具配置
│   │       └── scan_rules.yaml # 扫描规则
│   ├── ui/static/            # 前端静态资源
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   └── bin/
│       ├── receive.bat / .sh
│       └── validate.bat
```

### 1.3 代码规模评估

**Python 源码**：2,884 行，约 200-300 KB（未压缩源码）

**Hippocampus.exe**：~60 MB（PyInstaller 打包后的可执行文件，含 Python 运行时）

> 说明：当前 `Hippocampus.exe` 体积较大，因为 PyInstaller 将整个 Python 运行环境打包进去了。如果是纯 Python 分发（用户已有 Python 环境），exe 部分可以省略，体积可大幅缩小。

---

## 二、ChromaDB 存储占用估算

基于前一报告的分析，ChromaDB 存储需求取决于 schema 条目数量：

| 场景 | Schema 条目数 | ChromaDB 占用 | 说明 |
|------|------------|-------------|------|
| 轻度使用 | 0（不启用） | 0 | 纯 YAML/JSON 模式 |
| 入门 | 100 条 | ~5 MB | 含 HNSW 索引 |
| 标准使用 | 1,000 条 | ~40 MB | 适中规模 |
| 重度使用 | 10,000 条 | ~400 MB | 大规模记忆库 |

> 未实测，仅参考 ChromaDB 文档和社区数据。

---

## 三、Embedding 模型体积

### 3.1 常用小型 Embedding 模型

| 模型 | 体积 | 向量维度 | 语言支持 | 备注 |
|------|------|--------|--------|------|
| `all-MiniLM-L6-v2` | ~90 MB | 384 | 英文为主 | 不推荐中文场景 |
| `paraphrase-multilingual-MiniLM-L12-v2` | ~420 MB | 384 | **多语言（含中文）** | **推荐 USB 使用** |
| `text-embedding-3-small` | — | 1536 | 多语言 | OpenAI API，需联网 |

> 体积数据为 `sentence-transformers` 模型文件在磁盘的实际占用，未实测。

### 3.2 体积估算结论

**针对中文场景的推荐模型**：`paraphrase-multilingual-MiniLM-L12-v2`
- 体积：约 **400-500 MB**
- 向量维度：384 维
- 支持中文语义编码

**替代方案**（如果体积成问题）：
- 使用更小的模型（如 `all-MiniLM-L6-v2`，90 MB），但中文效果差
- 首次运行时从网络下载模型（需用户有网络）

---

## 四、小型 LLM 模型体积评估

### 4.1 候选模型对比

| 模型 | 体积（FP16/推荐） | 体积（INT4量化） | 参数量 | 中文能力 | 内存需求（推理） | 备注 |
|------|---------------|--------------|--------|--------|---------------|------|
| **Phi-3-mini** | ~2.3 GB | ~1.8 GB | 3.8B | 良好 | ~4-6 GB | Microsoft，微调版中文差 |
| **Qwen2-0.5B** | ~1 GB | ~600 MB | 0.5B | **优秀** | ~1-2 GB | 阿里巴巴，中文优化极佳 |
| **Phi-2** | ~1.5 GB | ~1 GB | 2.7B | 一般 | ~3-4 GB | Microsoft，已过时 |
| **ChatGLM3-6B** | ~6 GB | ~3.5 GB | 6B | 良好 | ~6-8 GB | 太大，不适合 USB |
| **TinyLlama-1.1B** | ~700 MB | ~600 MB | 1.1B | 一般 | ~1.5 GB | 开源轻量，中文弱 |
| **DeepSeek-Lite-1.8B** | ~1 GB | ~700 MB | 1.8B | 良好 | ~2 GB | 国产，中文较好 |

### 4.2 量化的影响

使用 `llama.cpp` 的 **INT4/INT8 量化**可大幅减少体积：
- FP16（半精度）：体积 = 原始模型大小
- INT8：体积减少约 30-40%
- INT4：体积减少约 50-60%，但质量略有下降

### 4.3 内存与 CPU 要求

**CPU 推理（无 GPU）**：

| 模型 | 量化等级 | 最低内存 | 推理速度（CPU） | 适用场景 |
|------|---------|---------|--------------|---------|
| Qwen2-0.5B | INT4 | 1.5 GB | ~10-20 tok/s | 轻量对话，本地使用 |
| Phi-3-mini | INT4 | 3 GB | ~8-15 tok/s | 质量优先 |
| TinyLlama-1.1B | INT4 | 800 MB | ~20-30 tok/s | 超轻量 |

> 速度数据为未实测，仅参考 llama.cpp 社区报告。

**Python + llama-cpp-python 依赖**：约 50-100 MB

---

## 五、存储空间汇总（三场景估算）

### 5.1 Scenario A：仅代码（无 LLM，无向量数据库）

**适用场景**：纯文件版，用户已有 Python 环境

| 组件 | 体积 |
|------|------|
| Python 源码 | ~300 KB |
| Hippocampus.exe（如含） | ~60 MB（当前打包方式） |
| 静态资源（UI/图标） | ~2 MB |
| 配置文件 | ~50 KB |
| SQLite 数据库 | ~100 KB（空库运行后） |
| 数据库存储（memory 数据） | 弹性：1-100 MB（取决于用户数据量） |
| **预留空间** | **50 MB** |
| **总计** | **约 65-170 MB** |

**结论**：8 GB USB 轻松覆盖，16 GB 绰绰有余。

### 5.2 Scenario B：代码 + ChromaDB 向量数据库

**适用场景**：V4 Auto-Extract + Schema 语义搜索功能

| 组件 | 体积 |
|------|------|
| 代码部分 | ~65 MB（来自 Scenario A） |
| ChromaDB 依赖 | ~100-150 MB |
| Embedding 模型（multilingual-MiniLM） | ~450 MB |
| ChromaDB 数据（1,000 条 schema） | ~40 MB |
| **预留空间** | **100 MB** |
| **总计** | **约 750-800 MB** |

**结论**：16 GB USB 足够，8 GB 紧张但勉强。

### 5.3 Scenario C：代码 + ChromaDB + 内嵌小 LLM

**适用场景**：离线 AI 助手模式，最大功能覆盖

| 组件 | 体积 |
|------|------|
| Scenario B 所有组件 | ~800 MB |
| LLM 模型（Qwen2-0.5B INT4） | ~700 MB |
| LLM 推理引擎（llama-cpp-python） | ~100 MB |
| LLM 运行临时缓存 | ~200 MB |
| **预留空间** | **200 MB** |
| **总计** | **约 2 GB** |

**结论**：16 GB USB 完全满足，32 GB 留有大量余量。

---

## 六、完整对比表

| 场景 | 代码 | ChromaDB | Embedding模型 | LLM模型 | 数据库存储 | 预留 | **总估算** | 推荐USB容量 |
|------|------|---------|--------------|--------|-----------|------|-----------|------------|
| **A** 仅代码 | ~65 MB | — | — | — | 弹性 | 50 MB | **~65-170 MB** | 8 GB ✅ |
| **B** +向量DB | ~65 MB | ~150 MB | ~450 MB | — | ~50 MB | 100 MB | **~750-800 MB** | 16 GB ✅ |
| **C** +向量DB+LLM | ~65 MB | ~150 MB | ~450 MB | ~700 MB | ~50 MB | 200 MB | **~1.8-2 GB** | 16 GB ✅ / 32 GB 充裕 |

---

## 七、USB 容量推荐

### 7.1 按用户场景推荐

| 用户场景 | 推荐容量 | 覆盖场景 |
|---------|---------|---------|
| 仅同步记忆文件，不需要 AI | **8 GB** | Scenario A（仅代码） |
| Schema 语义搜索，中等使用 | **16 GB** | Scenario B（+向量DB） |
| 离线 AI 助手，最大功能 | **32 GB** | Scenario C（+向量DB+LLM） |

### 7.2 实际建议

**对于 HIPPO V4 USB 版**：
1. **入门版（8 GB）**：仅代码分发，用户已有 Python 环境
2. **标准版（16 GB）**：含 ChromaDB + embedding 模型，涵盖 V4 Schema 功能
3. **全功能版（32 GB）**：额外含 Qwen2-0.5B LLM，支持离线 AI 对话

> 成本参考：2026 年 Q1，8 GB USB ≈ ¥20-30，16 GB ≈ ¥30-50，32 GB ≈ ¥50-80。

---

## 八、关键结论

1. **当前代码库（118 MB）已含 exe 打包**，实际纯源码仅约 2-3 MB
2. **ChromaDB 引入需要额外 ~600 MB**（含 embedding 模型），是最大的体积增长点
3. **小模型（Qwen2-0.5B INT4）约 700 MB**，在 USB 分发可行范围内
4. **Scenario C 全功能版约 2 GB**，16 GB USB 完全足够，留有充足余量
5. **建议首发版本采用 Scenario B**（16 GB），LLM 作为可选插件分发

---

**文档版本**：v1.0  
**数据来源**：基于当前代码库实际测量 + 公开模型规格（未实测）  
**建议**：正式发布前用真实模型文件验证体积数据