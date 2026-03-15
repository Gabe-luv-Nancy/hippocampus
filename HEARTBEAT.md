# HEARTBEAT.md

# 心跳巡检 - 静默模式

## 规则

1. 执行只读检查（Gateway状态、记忆备份完整性）
2. **如果一切正常：只回复 `HEARTBEAT_OK`**
3. **只有发现问题才详细汇报**

## 检查项目（轮换执行）

### A. Gateway 存活检查
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/health
```

### B. 记忆备份完整性检查
- 检查 `memory/YYYY-MM-DD.md` 是否存在（今天是2026-03-10）
- 检查文件是否有实质内容（>100字节）
- 检查 Git 状态是否有未提交的更改
- **频率**: 每天至少 1 次

## 状态追踪

在 `memory/heartbeat-state.json` 中记录检查时间：
```json
{
  "lastChecks": {
    "gateway": 1703275200,
    "memoryBackup": null
  }
}
```

## 输出规则

- 健康: `HEARTBEAT_OK`
- 异常: 详细说明问题（如 "Gateway 不可达" 或 "记忆文件未找到"）
