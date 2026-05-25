# SSL 证书申请与 Nginx HTTPS 配置指南

> 创建日期：2026-03-29
> 更新日期：2026-03-29

---

## 一、术语解释

| 术语 | 含义 |
|------|------|
| **SSL** | Secure Sockets Layer，数据加密传输协议 |
| **HTTPS** | HTTP + SSL，即加密版的 HTTP，地址栏显示小锁 🔒 |
| **证书（Certificate）** | 网站的"数字身份证"，证明域名属于你 |
| **TrustAsia** | 证书颁发机构（CA），类似 Let's Encrypt |
| **DV（Domain Validation）** | 域名验证型证书，只验证域名归属，最基础最快速 |
| **C1** | TrustAsia 的证书型号名称 |
| **Free（免费）** | DV 免费版，有效期 90 天 |
| **90天** | 免费证书有效期，到期前需续期 |
| **证书部署** | 将证书安装到 Nginx，让网站支持 HTTPS |
| **CRT 文件** | 证书主体文件（公钥） |
| **KEY 文件** | 私钥文件，**必须保密**，丢失无法恢复 |
| **TXT 记录** | DNS 解析的一种记录类型，用于验证域名归属 |

---

## 二、腾讯云免费 SSL 证书政策（2024年4月起）

| 项目 | 说明 |
|------|------|
| 免费额度 | 每账号 50 张 |
| 有效期 | 90 天（3个月） |
| 域名限制 | 无，可绑定任意域名 |
| 验证方式 | DNS 自动验证（推荐）|

**重要提醒：** 证书到期前需续期，腾讯云会发短信/邮件提醒。每 90 天续一次。

---

## 三、申请流程

### 3.1 提交申请

1. 登录 [腾讯云 SSL 证书控制台](https://console.cloud.tencent.com/ssl)
2. 点「证书管理」→「申请免费证书」
3. 填写信息：

| 字段 | 填写内容 |
|------|---------|
| 证书名称 | `gabe-luv-nancy.online` |
| 域名 | `gabe-luv-nancy.online` |
| 证书类型 | DV Basic 免费 |
| 验证方式 | **DNS 自动验证** ✅ |
| 所属项目 | 默认项目 |
| 标签 | 留空 |

4. 提交后等待审核（几小时到 1 个工作日）

### 3.2 DNS 自动验证

腾讯云会自动在 DNSPod 添加一条 TXT 记录，无需手动操作。

**TXT 记录示例：**
- 主机记录：`_dnsauth`
- 记录类型：TXT
- 记录值：`2026032813005339e1ln3jifsagjuquetc0dl0obstn3eun1dxiv01uqbfnk9yd5`

### 3.3 审核通过通知

腾讯云会通过短信和站内信通知：
> "您的域名 gabe-luv-nancy.online 的 TrustAsia C1 DV Free（90天）证书已审核通过并成功颁发。"

---

## 四、下载与部署流程

### 4.1 下载证书

1. 进入 [SSL 证书控制台](https://console.cloud.tencent.com/ssl)
2. 找到 `gabe-luv-nancy.online` 的证书
3. 点「下载」→ 选择「Nginx」格式
4. 解压 `.zip`，得到两个文件：

```
1_gabe-luv-nancy.online_bundle.crt   ← 证书文件（公钥）
2_gabe-luv-nancy.online_bundle.key    ← 私钥文件（保密！）
```

### 4.2 上传到云服务器

在本地 Terminal 执行：

```bash
# 创建目录
ssh root@81.70.200.211 "mkdir -p /root/clabin_sync/HIPPO/WEBSITE/ssl/"

# 上传证书
scp ~/下载路径/1_gabe-luv-nancy.online_bundle.crt root@81.70.200.211:/root/clabin_sync/HIPPO/WEBSITE/ssl/

# 上传私钥
scp ~/下载路径/2_gabe-luv-nancy.online_bundle.key root@81.70.200.211:/root/clabin_sync/HIPPO/WEBSITE/ssl/
```

> 注意：私钥文件（.key）属于敏感信息，不要发给别人，不要上传到公开的地方。

### 4.3 配置 Nginx

在云服务器上执行：

```bash
vi /etc/nginx/conf.d/clabin.conf
```

将配置内容替换为：

```nginx
# HTTP → HTTPS 强制跳转
server {
    listen       80;
    server_name  gabe-luv-nancy.online www.gabe-luv-nancy.online;
    return      301 https://$server_name$request_uri;
}

# HTTPS 主站
server {
    listen       443 ssl;
    server_name  gabe-luv-nancy.online www.gabe-luv-nancy.online;
    root         /root/clabin_sync/HIPPO/WEBSITE/www/html;
    index        index.html;

    # SSL 证书路径
    ssl_certificate     /root/clabin_sync/HIPPO/WEBSITE/ssl/1_gabe-luv-nancy.online_bundle.crt;
    ssl_certificate_key /root/clabin_sync/HIPPO/WEBSITE/ssl/2_gabe-luv-nancy.online_bundle.key;

    # 安全头
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        try_files $uri $uri/ =404;
    }

    location /assets/ {
        alias /root/clabin_sync/HIPPO/WEBSITE/www/html/assets/;
        expires 30d;
    }

    location /downloads/ {
        alias /root/clabin_sync/HIPPO/WEBSITE/www/html/downloads/;
        add_header Content-Disposition "attachment";
    }

    location ~ /\. {
        deny all;
    }
}
```

保存后重载配置：

```bash
nginx -t && nginx -s reload
```

---

## 五、验证结果

配置完成后访问以下地址，确认全部跳转到 HTTPS：

| 地址 | 预期结果 |
|------|---------|
| `http://www.gabe-luv-nancy.online/` | 301 重定向到 HTTPS |
| `https://www.gabe-luv-nancy.online/` | ✅ 显示网站，地址栏小锁 🔒 |
| `https://gabe-luv-nancy.online/` | ✅ 显示网站，地址栏小锁 🔒 |

本地验证命令：

```bash
curl -I http://www.gabe-luv-nancy.online/
# 应看到 HTTP/1.1 301 Moved Permanently

curl -I https://www.gabe-luv-nancy.online/
# 应看到 HTTP/2 200
```

---

## 六、证书续期流程（每 90 天）

1. 在证书到期前 30 天，腾讯云会发送续期提醒
2. 登录 SSL 控制台，找到即将过期的证书
3. 点「续期」，选择「DNS 自动验证」
4. 等待审核（几分钟）
5. 下载新证书，重新上传到云服务器
6. 执行 `nginx -s reload`

---

## 七、故障排查

| 现象 | 原因 | 解决方法 |
|------|------|---------|
| 浏览器提示证书无效 | 证书和域名不匹配 | 确认证书申请的是 `gabe-luv-nancy.online` |
| 访问 HTTP 不跳转 HTTPS | Nginx 未配置 80 端口重定向 | 检查 80 端口 server 块配置 |
| HTTPS 显示不安全 | 私钥文件路径错误 | 确认 `.key` 文件存在且路径正确 |
| 证书路径 404 | 文件未上传或路径错误 | `ssh` 到云端确认文件存在 |
