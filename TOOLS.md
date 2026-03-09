# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 硅基流动 API 脚本

### VLM 视觉理解
- **脚本:** `~/.openclaw/workspace/scripts/siliconflow-vlm.sh`
- **用法:** `./siliconflow-vlm.sh <图片路径或URL> "<提示词>"`
- **模型:** Qwen/Qwen2-VL-72B-Instruct
- **调用方式:** 通过子任务执行，不要直接修改 models.json！
- **示例:** `sessions_spawn` 任务中运行脚本，返回解析结果

### STT 语音识别
- 待创建脚本...
