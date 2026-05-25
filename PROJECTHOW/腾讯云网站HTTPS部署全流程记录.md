# 腾讯云网站 HTTPS 部署全流程记录

> 创建日期：2026-03-29
> 更新日期：2026-03-29

---

## 一、本次完成的工作

### 1.1 Nginx 安装与配置

- 安装 Nginx（yum install nginx）
- 创建网站目录结构 `/var/www/html/`
- 后来移动到 Syncthing 同步目录：`/root/clabin_sync/HIPPO/WEBSITE/www/html/`
- 创建 `/etc/nginx/conf.d/clabin.conf` 配置文件

### 1.2 权限问题解决

- nginx worker 以 nginx 用户运行，无权限读取 `/root/` 路径
- 解决方案：
  ```bash
  chmod o+x /root
  chmod -R o+r /root/clabin_sync/HIPPO/WEBSITE/www/html/
  ```

### 1.3 SSL 证书申请

- 在腾讯云 SSL 证书控制台申请免费 DV 证书
- 验证方式：DNS 自动验证（腾讯云自动添加 TXT 记录）
- 证书信息：
  - 颁发机构：TrustAsia
  - 型号：C1 DV Free
  - 有效期：90 天
- 审核通过时间：2026-03-29

### 1.4 证书文件

通过 Syncthing 同步上传到云端：
```
/root/clabin_sync/HIPPO/WEBSITE/ssl/
├── gabe-luv-nancy.online.crt          ← 证书文件
├── gabe-luv-nancy.online.key           ← 私钥文件
├── gabe-luv-nancy.online_bundle.crt   ← 证书包
├── gabe-luv-nancy.online_bundle.pem
└── gabe-luv-nancy.online.csr
```

### 1.5 Nginx HTTPS 配置

修改 `/etc/nginx/conf.d/clabin.conf`，监听 443 端口，配置 SSL 证书路径：
- 证书：`/root/clabin_sync/HIPPO/WEBSITE/ssl/gabe-luv-nancy.online_bundle.crt`
- 私钥：`/root/clabin_sync/HIPPO/WEBSITE/ssl/gabe-luv-nancy.online.key`
- HTTP 80 端口：301 重定向到 HTTPS
- HTTPS 443 端口：正常服务

---

## 二、待完成（用户操作）

### 2.1 腾讯云安全组开放 443 端口

**操作位置：** 腾讯云控制台 → 云服务器 → 安全组 → 入站规则

**添加规则：**
| 字段 | 值 |
|------|-----|
| 类型 | HTTPS |
| 协议 | TCP |
| 端口 | 443 |
| 来源 | 0.0.0.0/0 |
| 策略 | 允许 |

---

## 三、最终验证

安全组开放后，验证以下地址全部正常：

| 地址 | 预期结果 |
|------|---------|
| `https://www.gabe-luv-nancy.online/` | ✅ 显示网站，地址栏小锁 |
| `https://gabe-luv-nancy.online/` | ✅ 显示网站，地址栏小锁 |
| `http://www.gabe-luv-nancy.online/` | ✅ 301 重定向到 HTTPS |

---

## 四、相关文档清单（放在 HIPPO 文件夹下）

| 文档名 | 内容 |
|--------|------|
| `腾讯云基础概念与网站架构说明.md` | CVM/COS/控制台等基础概念 |
| `腾讯云网站部署完整操作手册.md` | Nginx 启停改、SSH/rsync 命令 |
| `SSH_RSYNC_Handbook.md` | SSH/rsync/scp 完整命令手册 |
| `SSL证书申请与Nginx配置指南.md` | SSL 证书申请与 HTTPS 配置详解 |
| `腾讯云网站HTTPS部署全流程记录.md` | 本文档，本次部署完整记录 |
