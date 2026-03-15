# 导入的配置记忆 (2026-02-26)

从 copied_md_to_corproate 导入的新配置点：

## 用户偏好
- 沟通风格：效率优先，有话直说，不需要比喻
- 称呼：bro
- 时区：UTC+8

## 项目工作规范
- 新需求 → 在 `projects/` 下新建文件夹
- 所有相关文件放同一文件夹

## 内存备份
- 仓库：Gabe-luv-Nancy/MyBroOpenClaw
- 频率：每周日 21:00 Asia/Shanghai

## API配置安全要点
- **不能直接改动 models.json** - 每次改动前必须先备份
- **改动前必须测试API** - 先用 curl 测试
- **401错误原因** - 配置错误或认证失败

## 语音识别 (STT)
- 硅基流动 SenseVoice
- 模型：FunAudioLLM/SenseVoiceSmall
- API Key: `sk-hgkxpbbusfstcyverghkfmljybhpnvpsxedisydtrhigwbro`
- 用途：飞书语音消息转文字

## 视觉智能 (VLM)
- 硅基流动 QVQ-72B-Preview / Qwen2-VL-72B-Instruct
- API Key 同上

## 服务稳定性 - 四重保障
1. 执行前强制备份
2. 沙盒环境测试
3. 心跳监控保命
4. 快速回滚机制

## 风险分级
- 🔴 高危：修改models.json、重启gateway
- 🟡 中危：安装新插件、添加新模型
- 🟢 低危：修改memory文件、更新文档

## 心跳任务
- 每日备份检查
- 系统健康检查 (每1小时)
