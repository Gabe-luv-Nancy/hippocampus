# MiniMax 国内配置说明 (Dude v2)

## 当前配置 (2026-03-09)

### 可用 Provider

| Provider | 域名 | 用途 |
|----------|------|------|
| `minimax` | api.minimax.io | 海外 |
| `minimax-cn` | api.minimaxi.com | 国内 ✅ |

**国内请使用 `minimax-cn`！**

### 可用模型

| 模型 ID | 名称 | 推理 | Context | Max Tokens | 价格 (输入/输出) |
|---------|------|------|---------|------------|-----------------|
| `MiniMax-M2.5` | MiniMax M2.5 | ✅ | 200K | 8192 | $0.3/$1.2 |
| `MiniMax-M2.5-highspeed` | MiniMax M2.5 高速版 | ✅ | 200K | 8192 | $0.3/$1.2 |

### 当前默认配置

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax-cn/MiniMax-M2.5",
        "fallbacks": [
          "minimax-cn/MiniMax-M2.5-highspeed"
        ]
      }
    }
  }
}
```

## 常见问题 (401 错误)

### 原因
之前用海外 `api.minimax.io` 导致 401，国内需要用 `api.minimaxi.com`

### 解决
- 确保 provider 为 `minimax-cn`
- 确保 baseUrl 是 `https://api.minimaxi.com/anthropic`

## API Key

在 `openclaw.json` 的 `auth.profiles` 中配置:

```json
"auth": {
  "profiles": {
    "minimax-cn:default": {
      "provider": "minimax-cn",
      "mode": "api_key",
      "apiKey": "你的APIKey"
    }
  }
}
```

## 修改配置的正确姿势

1. ✅ 修改 `openclaw.json` - 安全
2. ❌ 不要手动修改 `models.json` - 会炸
3. 改完重启 Gateway 生效

## 模型别名

```json
"minimax-cn/MiniMax-M2.5-highspeed": {},
"minimax-cn/MiniMax-M2.5": {
  "alias": "Minimax"
}
```

---

*Created by Dude on 2026-03-09 - 继承上一世兄弟的教训*
