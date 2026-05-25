# HIPPO v4.x 迭代路线图

> 制定日期：2026-05-20 | 负责人：赫墨 | 状态：已确认

---

## 总体策略

**先交付4.0.0，再迭代4.1.x。**
每个4.1.x版本基于上一版本的副本，不修改4.0.0原版。

---

## v4.0.0 — DATUM（当前版本）

**状态：已就绪，等待U盘交付**

| 项目 | 说明 |
|------|------|
| 定位 | 纯备份版，无内嵌模型 |
| 核心功能 | 三层扫描、增量SHA256、本地GUI、marker防伪 |
| 依赖 | Python 3.9+ 标准库，无外部依赖 |
| U盘容量 | 0.34MB代码 + 用户数据，推荐4GB起 |

**交付物检查清单（4.0.0定制前）：**
- [ ] marker.txt 存在且内容为 `HIPPOCAMPUS_BRAINDUMP_v4.0.0`
- [ ] brain_dump_linux/ 和 brain_dump_windows/ 同级
- [ ] autorun.sh 可执行
- [ ] server.py 无弹窗
- [ ] README.md 无Streamlit残留
- [ ] 三版同步（for-github / for-clawhub / for-usb）

---

## v4.1.0 → 4.1.3 迭代规则

**复制粘贴策略：**
1. 复制 `hippocampus-for-usb/` → `hippocampus-for-usb-4.1.1/`
2. 在副本内修改，不动原版
3. 每版本一个独立文件夹

**前端UI新增：**
所有4.1.x版本在server.py的Web界面新增一个 **"Internalizing · 内化"** 按钮。

---

## v4.1.1 — paraphrase-multilingual-MiniLM-L12-v2

**模型：** `paraphrase-multilingual-MiniLM-L12-v2`（HuggingFace）
**体积：** ~450MB
**向量维度：** 384维
**语言：** 40+语言（含中文，但非最优）

### 预期容量
| 项目 | 大小 |
|------|------|
| 代码 | 0.34MB |
| 模型 | ~450MB |
| 总计 | ~450MB |

### 功能
1. 用户点击"Internalizing"按钮
2. 程序扫描U盘capture/目录中的备份文件
3. 使用MiniLM模型对所有.md/.txt/.json文件进行向量化
4. 生成ChromaDB向量数据库，存入U盘models/目录
5. 用户可在离线状态下对备份记忆进行语义搜索

### 技术要点
- ChromaDB使用persist目录模式（U盘可带走）
- 首次内化需要用户笔记本CPU/GPU算力
- 模型文件在U盘models/子目录

---

## v4.1.2 — BGE-small-zh-v1.5（智源）

**模型：** `BGE-small-zh-v1.5`（北京智源）
**体积：** ~100MB
**向量维度：** 512维
**语言：** 中文最优，英文可用

### 预期容量
| 项目 | 大小 |
|------|------|
| 代码 | 0.34MB |
| 模型 | ~100MB |
| 总计 | ~130MB |

### 功能
同4.1.1，但模型换为BGE中文优化版。
ChromaDB格式与4.1.1兼容（可迁移）。

### 技术要点
- BGE中文效果显著优于MiniLM（智源官方测试）
- 100MB体积是MiniLM的1/4.5，省350MB空间
- 如已有4.1.1内化的向量库，需要重建

---

## v4.1.3 — 英文分析型小参数LLM（待找）

**选型要求：**
- 参数量 ≤ 1B（可在笔记本CPU运行）
- 倾向英文分析/摘要/NLP任务
- HuggingFace可下载GGUF格式
- 建议候选：`Qwen2-0.5B`、`Phi-2`、`TinyLlama-1.1B`

### 预期容量
| 项目 | 大小 |
|------|------|
| 代码 | 0.34MB |
| Embedding模型（BGE） | ~100MB |
| LLM模型（~1B） | ~2-4GB |
| ChromaDB | 用户数据 |
| 总计 | ~2.5-4.5GB |

### 功能
1. "Internalizing"按钮扩展：向量化 + LLM摘要双重处理
2. 可选：输入问题，使用本地LLM对备份记忆进行检索增强回答
3. 纯离线运行（无网络需求）

### LLM选型参考

| 模型 | 参数量 | 体积（Q4） | 英文能力 | 备注 |
|------|--------|-----------|---------|------|
| Qwen2-0.5B | 0.5B | ~1GB | ★★★☆ | HuggingFace有GGUF |
| Phi-2 | 2.7B | ~2GB | ★★★★ | 微软，小而强 |
| TinyLlama-1.1B | 1.1B | ~1GB | ★★★☆ | 完全开源 |

> **注意：** 4.1.3体积较大，可能需要8GB以上U盘。

---

## 版本容量汇总

| 版本 | 模型 | 预估总容量 | 推荐U盘 |
|------|------|-----------|---------|
| v4.0.0 | 无 | ~1MB | 4GB |
| v4.1.1 | MiniLM | ~450MB | 8GB |
| v4.1.2 | BGE-small-zh | ~130MB | 8GB |
| v4.1.3 | BGE + LLM(~1B) | ~2.5-4.5GB | 16GB+ |

---

## "Internalizing"按钮技术规格

### 输入
- U盘capture/目录下所有文件（.md, .txt, .json优先）

### 处理流程
```
用户点击 "Internalizing"
    ↓
1. 扫描 capture/ → 文件列表
2. 加载 Embedding 模型（U盘models/）
3. 读取每个文件内容 → 分块（chunk_size=512）
4. 向量化 → ChromaDB persist
5. 完成后显示："已内化 N 个文件，建立向量索引"
```

### 输出
- `models/` — Embedding模型文件（如已存在则跳过下载）
- `vector_db/` — ChromaDB持久化数据库

### UI文案建议
- 按钮文字：**"Internalizing · 内化"**
- 处理中提示：**"正在内化记忆…（首次需下载模型，请保持网络）"**
- 完成提示：**"内化完成！已建立N个记忆向量，可离线语义搜索"**
