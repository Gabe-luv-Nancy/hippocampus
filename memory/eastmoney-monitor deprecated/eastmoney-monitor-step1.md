# 东方财富网络监控 - 简明操作指南

---

## 第一步：查进程

打开 **PowerShell**，运行：

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*mainfutures*"}
```

实际显示结果：

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName

-------  ------    -----      -----     ------     --  -- -----------

   1259      95   365856     128552     670.27  54088  17 mainfutures

## 第二步：监控连接

把下面代码保存为 `monitor.ps1`：

```powershell
$processName = "mainfutures"  # ← 替换为第一步查到的进程名
$logFile = "$env:USERPROFILE\eastmoney\log.txt"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\eastmoney" | Out-Null

while ($true) {
    $pid = (Get-Process -Name $processName -ErrorAction SilentlyContinue).Id
    if (-not $pid) { Start-Sleep 3; continue }

    $conns = Get-NetTCPConnection -OwningProcess $pid -ErrorAction SilentlyContinue | 
        Where-Object {$_.State -eq "Established"}

    foreach ($c in $conns) {
        $line = "$(Get-Date -Format 'HH:mm:ss') | $($c.LocalAddress):$($c.LocalPort) -> $($c.RemoteAddress):$($c.RemotePort)"
        if (-not (Select-String -Path $logFile -Pattern "$($c.RemoteAddress):$($c.RemotePort)" -Quiet)) {
            Add-Content -Path $logFile -Value $line
            Write-Host $line
        }
    }
    Start-Sleep 5
}
```

---

## 第三步：运行

```powershell
powershell -ExecutionPolicy Bypass -File monitor.ps1
```

**输出：** 实时显示新的网络连接，保存到 `C:\Users\你的用户名\eastmoney\log.txt`

---

## 第四步：分析服务器

从日志中获取 **远程 IP:端口**，然后查询：

| 查询内容  | 网站                               |
| ----- | -------------------------------- |
| IP 归属 | https://ipinfo.io                |
| 端口用途  | https://www.speedguide.net/ports |



---

## 进阶：如果要抓完整数据包（Wireshark 详细教程）

如果 PowerShell 只能看到连接信息，要看**具体传输的数据内容**（如 WebSocket 消息、JSON 数据），需要用 Wireshark。

### 第一步：下载安装

1. **下载 Wireshark**：
   https://www.wireshark.org/download.html

2. **安装**：
   - 运行安装包
   - ⚠️ 勾选 **Install Npcap**（必须，管理员安装）
   - 其他选项默认

### 第二步：开始抓包

1. 打开 Wireshark
2. 双击 **"以太网"** 或 **"Wi-Fi"** 开始捕获
3. 顶部 filter 输入：`process.name == "mainfutures.exe"`
4. 运行东方财富期货
5. 点击红色方块 **停止**

### 第三步：过滤和分析

**常用过滤器：**

| 过滤器 | 作用 |
|--------|------|
| `tcp.port == 8000` | 只看 8000 端口 |
| `tcp.port in {8000..9000}` | 端口范围 |
| `websocket` | 只看 WebSocket |
| `json` | 只看 JSON 数据 |
| `ip.addr == 123.45.67.89` | 只看某 IP |

**追踪数据流：**

1. 右键点击一个 TCP 包
2. 选择 **"Follow" → "TCP Stream"**
3. 会看到完整的数据交互

### 第四步：导出数据

- **导出所有**：`File → Export Specified Packets → JSON`
- **导出选中**：`File → Export Specified Packets → Selected`

### 抓 WebSocket 特定说明

东方财富期货可能使用 WebSocket 长连接：

1. 过滤器：`websocket`
2. 或看端口：8000, 8080, 8443 等
3. 右键 → Follow TCP Stream 看到完整消息

### 常见端口参考

东方财富可能使用的端口（从日志获取后查询）：

| 端口 | 常见用途 |
|------|----------|
| 80/443 | HTTP/HTTPS |
| 8000-9000 | WebSocket |
| 8080 | HTTP 代理 |

---

## 故障排查

| 问题 | 解决方法 |
|------|----------|
| 找不到 mainfutures | 确认进程正在运行 |
| 没有网络包 | 检查 Npcap 是否安装 |
| 过滤不生效 | 确认语法正确（无引号） |
| 中文乱码 | Wireshark → Edit → Preferences → Character Set → UTF-8 |
