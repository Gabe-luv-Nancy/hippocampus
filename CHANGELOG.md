# Changelog

All notable changes to Hippocampus are documented here.

---

## 版本历史说明

**为什么直接从 v3.0 跳到 v3.2？**

- **v3.0**: 2026-03-21 首次创建（Photon 重塑品牌）
- **v3.1**: 2026-03-21 规划了但未实现（Micro-Macro 工作流、Achievement 系统）
- **v3.2**: 2026-04-05 实际发布新功能（Capture 抓取、Analyzer 分析、USB 支持）

v3.1 的规划已记录在 `ROADMAP_v3.1.md`，但因需求调整，功能合并到了 v3.2 中。

---

## [3.2.0] - 2026-04-05

### 新增

#### 记忆抓取模块 (`capture.py`)
- 自动扫描多路 AI 工具的记忆文件
- 支持：OpenClaw、豆包、元宝、讯飞星火、Kimi、通义千问、DeepSeek
- 通过 YAML 配置抓取路径
- 生成抓取清单 (manifest)

#### 本地分析模块 (`analyzer.py`)
- SQLite 向量数据库（TF-IDF 关键词搜索）
- 记忆索引和检索
- 摘要报告生成（JSON/Markdown）
- 本地模型接口（预留 Ollama/LM Studio 支持）

#### U盘产品支持 (`usb_manager.py`)
- Hippocampus U 盘自动检测
- 跨平台 autorun 脚本（Windows/macOS/Linux）
- OpenClaw 桥接协议（主机通信）
- 活动日志记录

#### U盘产品结构 (`U/`)
- `autorun.bat` - Windows 自动运行
- `autorun.sh` - macOS/Linux 自动运行
- `HIPPOCAMPUS_Marker.txt` - 产品标识

#### Clawhub 提示词版本 (`hippocampus-for-clawhub/`)
- `PROMPT.md` - 完整安装提示词
- `CLAWHUB.yaml` - Clawhub 上架配置

#### 开发流程文档 (`DEVELOPMENT.md`)
- 完整的开发步骤记录
- 用于生成 Clawhub 提示词注入版本

### 变更
- 双存储架构（Chronicle + Monograph）维持
- 增强关键词提取算法
- 改进搜索相关性评分

---

## [3.1.0] - 2026-03-21 (规划但未实现)

### 规划功能

#### Micro-Macro 工作流记忆
- 用户简短指令 → 完整操作流程的映射
- 例如："发文件" → "通过飞书发送，MD 格式"

#### Achievement/Achievement 成就系统
- 量化用户正向反馈
- 记录成功模式并复用

> ⚠️ **注意**: v3.1 的规划已合并到 v3.2 作为未来路线图参考。

---

## [3.0.0] - 2026-03-21

### 新增

#### Photon 重塑
- 全新哲学理念："AI 应修复人类记忆缺陷，而非模仿它们"
- 命令前缀从 `/hip` 改为 `/photon`
- 新增 `/photon graph` 命令查看知识图谱

#### 核心引擎重构
- 完整的 memory.py 重写
- SQLite 数据库索引增强

#### 双存储架构
- **Chronicle (时序记忆)**: 日常交互，自动保存
- **Monograph (重要事件)**: 重要决策、知识点，富元数据

#### 关键词索引
- 自动生成关键词索引文件
- 支持快速跨主题搜索

### 变更
- 所有命令重新设计
- `/hip` → `/photon`

---

## [2.2.0] - 2026-03-14

### 新增
- 双存储架构完成
- Monograph 系统（重要事件）
- 关键词索引文件

---

## [2.0.0] - 2026-03-01

### 新增
- SQLite 数据库索引
- 文件组织功能
- 关联生成器

---

## [1.0.0] - 2026-02-15

### 新增
- 初始版本发布
- 基础 Chronicle 功能
- Markdown 文件存储

---

## 关于版本号

Hippocampus 使用语义化版本 (Semantic Versioning):

- **MAJOR**: 架构重构，不兼容变更
- **MINOR**: 新功能，向后兼容
- **PATCH**: Bug 修复

版本从 3.0 开始是因为 Photon 是一个重要的品牌重塑，代表了理念的根本转变。
