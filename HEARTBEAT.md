# HEARTBEAT.md

# 心跳巡检 - 静默模式

## 规则

1. 执行只读检查（Gateway状态、API连通性）
2. **如果一切正常：只回复 `HEARTBEAT_OK`**
3. **只有发现问题才详细汇报**

## 检查命令

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/health
```

## 输出规则

- 健康: `HEARTBEAT_OK`
- 异常: 详细说明问题（如 "Gateway 不可达"）
