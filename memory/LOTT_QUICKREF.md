# LOTT 项目快速参考

## 常用路径

| 资源 | Windows 路径 | WSL 路径 |
|------|-------------|----------|
| 项目根目录 | `X:\LOTT` | `/mnt/x/LOTT` |
| 数据源 | `X:\LOTT\src\Data\DataSource` | `/mnt/x/LOTT/src/Data/DataSource` |
| TimescaleDB | `X:\LOTT\src\Data\DataSource\TimescaleDB` | 同左 |
| 测试 | `X:\LOTT\tests` | `/mnt/x/LOTT/tests` |

## 快速命令

### WSL 端 (我在这里执行)
```bash
# 进入项目
cd /mnt/x/LOTT

# 查看文件
ls -la /mnt/x/LOTT/src/Data/DataSource/TimescaleDB/

# 读取文件
cat /mnt/x/LOTT/src/Data/DataSource/TimescaleDB/README.md
```

### Windows 端 (你在 VS Code + Cline 执行)
```bash
# Cline 快捷键
Ctrl+Shift+P -> Cline: New Conversation

# 终端命令
conda activate LOTT
pytest tests/
```

## 当前任务状态

### 已完成 ✅
- [x] TimescaleDB 配置目录创建
- [x] YAML 配置文件
- [x] Python 配置类
- [x] 数据库客户端
- [x] README 说明文档

### 待完成 ⏳
- [ ] Cline 集成测试
- [ ] 集成到数据服务
- [ ] 创建使用示例

## 下一步行动

1. **验证 TimescaleDB 容器运行**
   - 在 Docker Desktop 查看是否有 timescaledb 容器运行
   
2. **测试连接**
   - 运行 Python 测试连接

3. **选择 Cline 任务**
   - 从 `LOTT_CLINE_TEMPLATES.md` 选择模板
   - 在 Cline 中执行

---

*最后更新: 2026-03-11 20:50*
