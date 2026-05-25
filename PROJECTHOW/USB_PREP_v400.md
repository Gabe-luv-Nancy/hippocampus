# HIPPO v4.0.0 U盘预装清单

> 制定日期：2026-05-20 | 状态：等待鱼总确认
> ⚠️ 鱼总U盘下单前请确认此清单

---

## U盘预装内容（v4.0.0）

### brain_dump_linux/
**不含内容（已剔除）：**
- ✗ `_deprecated/Hippocampus_elf_deprecated`（117MB旧二进制，废弃）
- ✗ `__pycache__/*.pyc`（Python字节码缓存，用户环境自动生成）
- ✗ `_deprecated/streamlit_app.cpython-311.pyc`（43KB，废弃）

**必须包含（干净代码）：312KB**

| 路径 | 类型 | 说明 |
|------|------|------|
| `brain_dump_linux/autorun.sh` | 脚本 | 交互式启动菜单，可执行 |
| `brain_dump_linux/server.py` | Python | HTTP REST API + 本地GUI（无弹窗） |
| `brain_dump_linux/marker.txt` | 标识 | 内容：`HIPPOCAMPUS_BRAINDUMP_v4.0.0` |
| `brain_dump_linux/lib/scanner.py` | 模块 | 三层扫描引擎（Phase 0/1/2） |
| `brain_dump_linux/lib/memory_scanner.py` | 模块 | AI记忆扫描器 |
| `brain_dump_linux/lib/agent_snapshot.py` | 模块 | Agent发现+记忆快照 |
| `brain_dump_linux/lib/detector.py` | 模块 | AI工具检测（12+工具） |
| `brain_dump_linux/lib/ssh_scanner.py` | 模块 | SSH/SFTP远程扫描 |
| `brain_dump_linux/lib/rules_engine.py` | 模块 | 规则匹配引擎 |
| `brain_dump_linux/lib/file_hasher.py` | 模块 | SHA256哈希 |
| `brain_dump_linux/lib/usb_detector.py` | 模块 | U盘检测 |
| `brain_dump_linux/lib/json_log.py` | 模块 | JSON Lines日志 |
| `brain_dump_linux/lib/config/ai_tools.yaml` | 配置 | AI工具路径配置 |
| `brain_dump_linux/lib/config/scan_rules.yaml` | 配置 | 扫描规则 |
| `brain_dump_linux/db/init_db.py` | 脚本 | 数据库初始化/校验 |
| `brain_dump_linux/db/brain_dump.sqlite` | 数据库 | 预建SQLite（0KB或小占位） |
| `brain_dump_linux/bin/receive.sh` | 脚本 | 数据接收脚本 |
| `brain_dump_linux/ui/static/index.html` | 前端 | Web UI首页 |
| `brain_dump_linux/ui/static/app.js` | 前端 | Web UI逻辑 |
| `brain_dump_linux/ui/static/style.css` | 前端 | Web UI样式 |
| `brain_dump_linux/_deprecated/streamlit_app.py` | 归档 | 旧Streamlit源码（参考用） |
| `brain_dump_linux/_archived_windows_files/` | 归档 | 旧Windows批处理（参考用） |
| `brain_dump_linux/capture/` | 目录 | **自动创建**，勿预置文件 |
| `brain_dump_linux/output/` | 目录 | **自动创建**，勿预置文件 |
| `brain_dump_linux/logs/` | 目录 | **自动创建**，勿预置文件 |

---

### brain_dump_windows/
**必须包含：52KB**

| 路径 | 类型 | 说明 |
|------|------|------|
| `brain_dump_windows/autorun.bat` | 批处理 | 主启动器（WSL桥接） |
| `brain_dump_windows/1-本地版.bat` | 批处理 | 一键扫描本机 |
| `brain_dump_windows/2-U盘版.bat` | 批处理 | 扫描指定U盘 |
| `brain_dump_windows/wsl_bridge.py` | Python | Win↔WSL路径桥接 |
| `brain_dump_windows/marker.txt` | 标识 | 内容：`HIPPOCAMPUS_BRAINDUMP_v4.0.0` |
| `brain_dump_windows/bin/receive.bat` | 批处理 | 数据接收 |
| `brain_dump_windows/bin/validate.bat` | 批处理 | 数据校验 |
| `brain_dump_windows/capture/` | 目录 | **自动创建** |
| `brain_dump_windows/output/` | 目录 | **自动创建** |
| `brain_dump_windows/logs/` | 目录 | **自动创建** |

---

### 根目录文件

| 路径 | 类型 | 说明 |
|------|------|------|
| `README.md` | 文档 | 产品说明（来自hippocampus-for-usb/README.md） |
| `marker.txt` | 标识 | U盘根目录，内容：`HIPPOCAMPUS_BRAINDUMP_v4.0.0`（可选，双保险） |

---

## 预装总大小

| 项目 | 大小 |
|------|------|
| brain_dump_linux/（干净代码） | ~312KB |
| brain_dump_windows/ | ~52KB |
| README.md | ~14KB |
| 预装合计 | **~400KB** |
| 推荐U盘容量 | **4GB**（4GB够用，8GB起步更稳妥） |

> ⚠️ **4.1.x版本需重新评估：**
> - v4.1.1（MiniLM）：~450MB → 需要8GB
> - v4.1.2（BGE-small-zh）：~130MB → 8GB够用
> - v4.1.3（BGE+LLM）：~2.5-4.5GB → 16GB+

---

## U盘目录结构（预装后）

```
X:（U盘根目录）/
├── marker.txt                    ← 内容：HIPPOCAMPUS_BRAINDUMP_v4.0.0
├── README.md                      ← 产品说明
│
├── brain_dump_linux/             ← Linux原生版（312KB）
│   ├── autorun.sh                ← 可执行
│   ├── server.py                 ← 无弹窗GUI
│   ├── marker.txt                ← 同上
│   ├── lib/
│   │   ├── scanner.py            ← 三层扫描
│   │   ├── memory_scanner.py
│   │   ├── agent_snapshot.py
│   │   ├── detector.py
│   │   ├── ssh_scanner.py
│   │   ├── rules_engine.py
│   │   ├── file_hasher.py
│   │   ├── usb_detector.py
│   │   ├── json_log.py
│   │   └── config/
│   │       ├── ai_tools.yaml
│   │       └── scan_rules.yaml
│   ├── db/
│   │   ├── init_db.py
│   │   └── brain_dump.sqlite
│   ├── bin/
│   │   └── receive.sh
│   ├── ui/static/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── style.css
│   ├── _deprecated/              ← 旧streamlit_app.py（归档）
│   ├── _archived_windows_files/  ← 旧批处理（归档）
│   ├── capture/                 ← [自动创建]
│   ├── output/                  ← [自动创建]
│   └── logs/                    ← [自动创建]
│
└── brain_dump_windows/           ← Windows WSL版（52KB）
    ├── autorun.bat
    ├── 1-本地版.bat
    ├── 2-U盘版.bat
    ├── wsl_bridge.py
    ├── marker.txt
    ├── bin/
    │   ├── receive.bat
    │   └── validate.bat
    ├── capture/                 ← [自动创建]
    ├── output/                  ← [自动创建]
    └── logs/                   ← [自动创建]
```

---

## 定制前检查清单

- [ ] 剔除`_deprecated/Hippocampus_elf_deprecated`（117MB废弃二进制）
- [ ] 剔除所有`__pycache__/`目录
- [ ] 剔除`streamlit_app.cpython-311.pyc`（字节码缓存）
- [ ] `autorun.sh`已设置可执行权限（`chmod +x`）
- [ ] `brain_dump_linux/marker.txt`内容：`HIPPOCAMPUS_BRAINDUMP_v4.0.0`
- [ ] `brain_dump_windows/marker.txt`内容：`HIPPOCAMPUS_BRAINDUMP_v4.0.0`
- [ ] Linux版和Windows版**同级**放在U盘根目录
- [ ] `capture/`、`output/`、`logs/`目录为空（自动创建）

---

## 定制后验证命令（WSL/Linux环境）

```bash
# 1. 验证marker
cat /path/to/usb/marker.txt
# 预期：HIPPOCAMPUS_BRAINDUMP_v4.0.0

# 2. 验证目录结构
ls /path/to/usb/
# 预期：brain_dump_linux/  brain_dump_windows/  README.md  marker.txt

# 3. 验证Linux脚本可执行
test -x /path/to/usb/brain_dump_linux/autorun.sh && echo "OK" || echo "NOT EXECUTABLE"

# 4. 验证没有117MB垃圾
du -sh /path/to/usb/brain_dump_linux/
# 预期：< 2M（不含废弃ELF）

# 5. 运行扫描测试
cd /path/to/usb/brain_dump_linux/
python3 lib/scanner.py scan --path /home/ --output output/
```

---

## U盘下单建议

| 项目 | 建议 |
|------|------|
| **v4.0.0首发版** | 4GB（鱼总反馈供应商可能无4GB产线）→ **8GB起步** |
| v4.1.1 | 8GB（MiniLM ~450MB） |
| v4.1.2 | 8GB（BGE ~130MB） |
| v4.1.3 | 16GB+（BGE + LLM ~2.5-4.5GB） |

**首批U盘（v4.0.0）：推荐8GB USB 3.0，兼顾价格和留余量。**
