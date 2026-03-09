# 东方财富期货网络监控指南

> 目标：自主可控地了解东方财富期货软件的数据传输机制

---

## 方法一：进程网络监控（最简单，推荐先做）

### 步骤 1：找到进程信息

打开 **PowerShell** 或 **CMD**，运行：

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*eastmoney*"} | Select-Object Name, Id, Company
```

常见进程名：
- `eastmoney.exe`
- `EFutures.exe`
- `DFCF.exe`
- `Futures.exe`

记下进程 ID（PID）。

---

### 步骤 2：监控网络连接

```powershell
# 查看该进程的所有网络连接
netstat -ano | findstr "进程ID"

# 或用 PowerShell（更详细，每3秒刷新）
while($true) { 
    Get-NetTCPConnection -OwningProcess 进程ID -ErrorAction SilentlyContinue | 
        Where-Object {$_.State -eq "Established"} |
        Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort
    Start-Sleep -Seconds 3
    Clear-Host
}
```

这会显示：
- 本地 IP:端口
- 远程 IP:端口（东方财富服务器）
- 连接状态

---

### 步骤 3：保存连接日志

创建脚本 `monitor-connections.ps1`：

```powershell
# monitor-connections.ps1

# ===== 配置 =====
$processName = "eastmoney"  # 根据实际情况修改进程名（不含 .exe）
$outputDir = "$env:USERPROFILE\eastmoney_monitor"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# ===== 主循环 =====
Write-Host "=========================================="
Write-Host "  东方财富网络连接监控器"
Write-Host "=========================================="
Write-Host "进程名: $processName"
Write-Host "输出目录: $outputDir"
Write-Host "按 Ctrl+C 停止"
Write-Host ""

$logFile = "$outputDir\connections_$(Get-Date -Format 'yyyyMMdd').log"
$jsonDir = "$outputDir\json_data"
New-Item -ItemType Directory -Force -Path $jsonDir | Out-Null

function Get-ProcessPID {
    $p = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($p) { return $p.Id }
    return $null
}

$seenConnections = @{}

while ($true) {
    $pid = Get-ProcessPID
    
    if (-not $pid) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠️ 进程未运行，等待中..."
        Start-Sleep -Seconds 3
        continue
    }
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Write-Host "[$timestamp] 📡 PID: $pid"
    
    # 获取 TCP 连接
    $tcpConns = Get-NetTCPConnection -OwningProcess $pid -ErrorAction SilentlyContinue | 
        Where-Object {$_.State -eq "Established"}
    
    # 获取 UDP 端点
    $udpConns = Get-NetUDPEndpoint -OwningProcess $pid -ErrorAction SilentlyContinue
    
    $newConnections = @()
    
    foreach ($conn in $tcpConns) {
        $key = "$($conn.RemoteAddress):$($conn.RemotePort)"
        
        if (-not $seenConnections.ContainsKey($key)) {
            $seenConnections[$key] = $true
            $newConnections += $conn
            
            $info = "$timestamp | TCP | $($conn.LocalAddress):$conn.LocalPort -> $($conn.RemoteAddress):$conn.RemotePort"
            Write-Host "  ✅ $info"
            Add-Content -Path $logFile -Value $info
        }
    }
    
    foreach ($conn in $udpConns) {
        $key = "UDP:$($conn.RemoteAddress):$($conn.RemotePort)"
        
        if (-not $seenConnections.ContainsKey($key)) {
            $seenConnections[$key] = $true
            
            $info = "$timestamp | UDP | $($conn.LocalAddress):$conn.LocalPort -> $($conn.RemoteAddress):$conn.RemotePort"
            Write-Host "  ✅ $info"
            Add-Content -Path $logFile -Value $info
        }
    }
    
    Write-Host "  已发现 $($seenConnections.Count) 个唯一连接"
    Write-Host ""
    
    Start-Sleep -Seconds 5
}
```

**使用方法：**

1. 复制上面的代码，保存为 `monitor-connections.ps1`
2. 打开 PowerShell（右键 → 以管理员身份运行）：
   ```powershell
   cd 脚本所在目录
   powershell -ExecutionPolicy Bypass -File monitor-connections.ps1
   ```
3. 会生成：
   - `connections_20260305.log` - 连接日志
   - `json_data/` - 后续用于存放抓取的数据

---

## 方法二：HTTP/HTTPS 流量抓包（需要工具）

### 方案 A：使用 Microsoft Network Monitor（推荐，比 Wireshark 轻量）

1. **下载**：
   https://www.microsoft.com/en-us/download/details.aspx?id=4865

2. **安装后**：
   - 打开 Network Monitor
   - 选择 "New Capture"
   - 点击 "Start"
   - 过滤：`ProcessName == 'eastmoney.exe'`

3. **查看数据**：
   - 展开帧数据
   - 找 HTTP/HTTPS 内容

---

### 方案 B：使用 Wireshark（功能最强）

1. **下载**：
   https://www.wireshark.org/download.html

2. **安装时**：
   - 勾选 "Install Npcap"（需要管理员安装）
   - 其他默认

3. **抓包步骤**：
   ```
   a. 打开 Wireshark
   b. 双击 "以太网" 或 "Wi-Fi" 开始捕获
   c. 在 filter 框输入: http or tls
   d. 找到东方财富进程:
      - Windows: 菜单 Capture → Options → 在 "Capture filter" 输入:
        process.name == "eastmoney.exe"
      - 或捕获后过滤: ip.addr == "服务器IP"
   e. 点击红色方块停止
   ```

4. **导出数据**：
   - File → Export Specified Packets → JSON 格式

---

### 方案 C：浏览器开发者工具（如果是 WebView 版本）

如果东方财富期货有网页版：
1. 打开 Chrome/Firefox
2. F12 打开开发者工具
3. 切换到 Network 标签
4. 访问东方财富网页
5. 右键 → Save all as HAR

---

## 方法三：WebSocket 专项监控

东方财富期货可能使用 WebSocket 长连接。

### 使用 PowerShell 监控 WebSocket：

```powershell
# 检查端口 8000-9000 范围的 WebSocket 连接
$ports = 8000..9000
$wsConnections = @()

foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
        Where-Object {$_.State -eq "Established"}
    
    foreach ($conn in $conns) {
        $wsConnections += $conn
    }
}

$wsConnections | Format-Table
```

### 使用 Wireshark 过滤 WebSocket：

```
tcp.port == 8000 || tcp.port == 8080 || tcp.port == 8443
```

---

## 常见服务器地址参考

东方财富可能的服务器（从连接日志中获取）：

```
# 常见的东方财富服务器域名（待确认）
push2.eastmoney.com
push.eastmoney.com
quotation.eastmoney.com
data.eastmoney.com
```

**获取后**：可以在以下网站查询 IP 归属：
- https://ipinfo.io
- https://www.ip138.com

---

## 数据保存建议

| 文件类型 | 用途 | 格式 |
|----------|------|------|
| `connections_*.log` | 连接记录 | 纯文本 |
| `*.pcap / *.cap` | 原始数据包 | 二进制 |
| `*.har` | HTTP 归档 | JSON |
| `traffic_*.json` | 流量摘要 | JSON |

**重要**：
- 所有抓取的数据建议保存在本地，不要上传到云
- 定期清理，避免硬盘占满
- 敏感数据（如果有）妥善保管

---

## 故障排查

| 问题 | 解决方法 |
|------|----------|
| 进程名找不到 | 打开任务管理器，详细查看进程名称 |
| 权限不足 | PowerShell 用管理员身份运行 |
| 抓不到数据 | 确认进程确实有网络活动 |
| Wireshark 无法启动 | 需要安装 Npcap（管理员安装） |
| 端口被占用 | 换一个端口或关闭冲突程序 |

---

## 下一步

1. **先用方法一** 运行脚本，确认东方财富期货的进程名和连接
2. **记录下服务器 IP/域名**
3. **根据需要** 安装 Wireshark 深入抓包
4. **分析数据格式**（如果是 JSON，保存下来用编辑器打开）

---

需要我帮你根据实际运行结果继续分析吗？
