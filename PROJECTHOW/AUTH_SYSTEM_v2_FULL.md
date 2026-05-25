# HIPPO 商业分发与授权系统 v2.0

## Hippocampus Business Distribution & License System

> 版本：v2.0
> 制定：2026-05-21
> 状态：v2.1 已修订

---

## 一、系统全景

> **物理世界对象清单：**
>
> | # | 对象 | 说明 | 状态 |
> |---|------|------|------|
> | 1 | 空白产品副本 | 可供复制分发、尚未嵌入Incantation的程序包 | U盘版+下载版 |
> | 2 | 用户U盘 | 已烧录Grimoire的物理介质，快递到用户 | 实物发货 |
> | 3 | 用户电脑 | 运行Hippocampus的终端，纯本地操作 | 用户自有 |
> | 4 | 鱼总工作站 | 运行keygen/burn_usb的Admin端 | 实验室 |
> | 5 | 云服务器 | 公网暴露的网站+API+DB | 腾讯云 |

```
┌─────────────────────────────────────────────────────────────┐
│                        用户侧                               │
│                                                             │
│   网站注册页              用户U盘             App本地     │
│   token申请表单    →    物理发货    →    Incantation校验        │
│   付费接口                key已植入            每次操作验    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 快递/物流
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      鱼总（商家）侧                          │
│                                                             │
│   Admin工具              U盘烧录            邮件通知         │
│   keygen.py         burn_usb.py        发送下载链接          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTPS (公网)
                              │
┌─────────────────────────────────────────────────────────────┐
│              云服务器 · gabe-luv-nancy.online                       │
│                                                             │
│   WEB层 · gabe-luv-nancy.online        API层 · 同域名/api/            │
│   网站前端                        REST API                   │
│   付费接口                        用户管理                   │
│   下载分发                        密钥生成（备用）           │
│                                                             │
│   DB层 · SQLite                                              │
│   用户数据库                                              │
│   订单记录                                                │
│   Incantation库                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心概念定义

**Spell-origin**

**Sigil**​ (符文)

**定义：**​ 用户自定义的“真言”。  
**规则：**  

1. 长度8-20位，必须是大小写字母与数字混合。  
2. 建议格式：`[昵称缩写] + [特殊日期] + [随机盐值]`(例: `Ai26Lv99`)。  
3. 这是你的“灵魂印记”，公开可见但无法反推密钥。

**Spell-distro**​

**Incantation**​ (咒语)

**定义：**​ 激活用的“解封咒”。  
**格式：**​ `XXXX-XXXXXXXXXXXXXXXX-XXXX`  
**示例：**​ `MAGE-K7G2X9P0Q3R1T...-0521`

**.hippo_license**​

**Grimoire**​ (魔法书/卷轴)

**定义：**​ 本地存储的Grimoire授权凭证。  
**内容：**​ 存放着加密的Spell-origin哈希与契约期限，如同记载秘密的羊皮纸。

**Arcanum**​

**Arcanum**​ (至高奥秘)

**定义：**​ 鱼总持有的“创世源码”。  
**特性：**​ 绝不离线的32字节神器，是所有咒语力量的源泉。

**Rune**​

**Rune**​ (符文标记)

**定义：**​ 官方的“纪元标记”。  
**作用：**​ 如 `HP2026`。一旦更换符文，旧咒语全部失效，开启新纪元。

### 2.1 Spell-origin（魔咒，like a spell word, works everywhere）

```
用户自设身份标识，同时作为Incantation的签名种子。

设定规则：
  1. 长度 8-20 位，仅允许大小写英文字母（A-Z, a-z）与数字（0-9），不含空格和特殊符号
  2. 必须同时包含至少 1 个大写字母、1 个小写字母、1 个数字（三类缺一不可）
  3. 建议格式：[昵称缩写] + [特殊日期] + [随机盐值]（例：Ai26Lv99）
  4. 不可与已有用户的 Spell-origin 重复（注册时服务端校验）

性质：公开可见，但无法反推 Arcanum 或 Incantation
```

### 2.2 Spell-distro（Activation Key）

```
由鱼总Arcanum签名的HMAC-SHA256签名
包含：Spell-origin+Rune+到期日+签名
格式：XXXX-XXXXXXXXXXXXXXXX-XXXX
示例：FISH-JBSWY3DPEHPK3PXP-0521
```

### 2.3 Grimoire（.hippo_license 魔法书）

```
存储在用户本地的JSON文件
包含：Spell-origin的哈希（原文不出现在磁盘）、Incantation、到期日、功能列表
```

### 2.4 Arcanum（至高奥秘）

```
存储在鱼总本地（绝不离线分发）
HMAC-SHA256的密钥种子
32字节，Base64编码后约44字符
鱼总持有，用于给每个用户的Incantation签名
```

### 2.5 Rune（符文标记）

```
官方标识字符，如"HP2026"
所有Incantation使用同一个Rune
更换Rune = 所有旧Incantation失效（新商业周期开始时）
```

---

## 三、商业流程

### 3.1 用户注册 → U盘发货（全流程）

```
用户                                         鱼总(Admin)                          云服务器
  │                                              │                                    │
  │  ① 访问gabe-luv-nancy.online                        │                                    │
  │     填写Spell-origin（Fish2026）                     │                                    │
  │     邮箱选填                                  │                                    │
  │  ② 付费 $XX                                   │                                    │
  │     （Stripe/本地支付）                       │                                    │
  │                                              │                                    │
  │  ③ 订单提交 ──────────────────────────────► │                                    │
  │     POST /api/orders                         │                                    │
  │     { token, email?, payment_id }            │                                    │
  │                                              │                                    │
  │                                           ④ 收到邮件/订单通知                     │
  │                                              │  运行 burn_usb.py:                  │
  │                                              │  python3 burn_usb.py \              │
  │                                              │    --spell-origin Fish2026 \               │
  │                                              │    --device /dev/sdX \               │
  │                                              │    --days 365                       │
  │                                              │                                    │
  │                                              │  ⑤ U盘烧录:                        │
  │                                              │  - 格式化U盘                        │
  │                                              │  - 复制程序                         │
  │                                              │  - 生成Incantation                       │
  │                                              │  - 写入.hippo_license               │
  │                                              │  - 验证完整性                       │
  │                                              │                                    │
  │                                           ⑥ 快递发货                             │
  │                                              │                                    │
  │  ⑦ 收到U盘                                  │                                    │
  │     双击 Hippocampus                         │                                    │
  │     → 自动读取.hippo_license                │                                    │
  │     → 校验通过                               │                                    │
  │     → 使用产品                               │                                    │
```

### 3.2 用户注册 → 下载版（全流程）

```
用户                                         云服务器
  │                                              │
  │  ① 访问gabe-luv-nancy.online                        │
  │     填写Spell-origin（Fish2026）                     │
  │     邮箱选填                                  │
  │  ② 付费 $XX                                   │
  │  ③ 订单提交                                  │
  │     POST /api/orders                         │
  │                                              │
  │                                           ④ 立即处理:
  │                                              │  - 验证Spell-origin唯一性
  │                                              │  - 生成Incantation
  │                                              │  - 将Incantation写入程序包
  │                                              │  - 生成唯一下载链接
  │                                              │
  │  ⑤ 下载链接发送至邮箱（选填）                │
  │     你的下载链接: https://gabe-luv-nancy.online/
  │     download/Fish2026/hippocampus-v4.0.zip  │
  │                                              │
  │  ⑥ 用户下载、解压                           │
  │     双击 Hippocampus                         │
  │     → Incantation已植入                           │
  │     → 使用产品                               │
```

### 3.3 用户续费

```
用户                                         鱼总/云服务器
  │                                              │
  │  ① 产品内提示"授权到期"                      │
  │  ② 联系鱼总/访问续费页                       │
  │  ③ 付费                                      │
  │  ④ 新Incantation生成                               │
  │     U盘版: 鱼总重新burn到同一U盘              │
  │     下载版: 发送新下载链接（覆盖安装）        │
  │  ⑤ 用户获得新授权                            │
```

---

## 四、技术架构

### 4.1 云服务器端

```
┌──────────────────────────────────────────────────┐
│               云服务器 (VPS/云主机)               │
│                   公网IP: X.X.X.X                 │
│                                                  │
│  ┌────────────────┐    ┌──────────────────────┐ │
│  │  Nginx/Caddy   │───►│  FastAPI/Flask      │ │
│  │  反向代理+SSL   │    │  REST API Backend   │ │
│  │  :80, :443     │    │  (Python)           │ │
│  └────────────────┘    └──────────────────────┘ │
│          │                      │                │
│          ▼                      ▼                │
│  ┌────────────────┐    ┌──────────────────────┐ │
│  │  静态网站       │    │  SQLite/PostgreSQL  │ │
│  │  HTML/CSS/JS   │    │  用户DB             │ │
│  │  付费页面       │    │  订单DB             │ │
│  │  下载分发       │    │  IncantationDB           │ │
│  └────────────────┘    └──────────────────────┘ │
│                                                  │
│  域名: gabe-luv-nancy.online（已备案+SSL）          │
└──────────────────────────────────────────────────┘
```

**推荐配置：**

- 已有：腾讯云轻量应用服务器（gabe-luv-nancy.online）
- SSL证书：TrustAsia C1 DV Free（已配置）

### 4.2 服务分层

| 服务    | 暴露方式     | 域名                           | 端口     | 说明            |
| ----- | -------- | ---------------------------- | ------ | ------------- |
| 静态网站  | HTTPS    | gabe-luv-nancy.online       | 80/443 | 用户看到的网站       |
| API服务 | HTTPS    | gabe-luv-nancy.online/api/  | 443    | REST API，内部逻辑 |
| 管理后台  | HTTPS+密码 | gabe-luv-nancy.online/admin/| 443    | 鱼总管理界面        |
| 下载分发  | HTTPS    | gabe-luv-nancy.online/dl/   | 443    | 动态打包下载        |

### 4.3 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash      TEXT NOT NULL UNIQUE,       -- SHA256(spell_origin.lower())
    token_display   TEXT NOT NULL,               -- 显示用（首尾明文，中间***隐藏）
    email           TEXT,                         -- 选填，仅用于推广
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    status          TEXT DEFAULT 'active',        -- active/suspended/expired
    source          TEXT DEFAULT 'website',       -- website/usb/manual
    notes           TEXT                          -- 备注
);

-- Incantation表
CREATE TABLE activations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER REFERENCES users(id),
    incantation     TEXT NOT NULL UNIQUE,        -- Incantation（Incantation）
    expires_at      DATE NOT NULL,
    rune            TEXT NOT NULL,               -- Rune（符文标记，如HP2026）
    machine_id      TEXT,                         -- 可选，机器绑定
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by      TEXT DEFAULT 'admin',         -- admin/system/usb_burn
    is_active       BOOLEAN DEFAULT TRUE,
    is_revoked      BOOLEAN DEFAULT FALSE
);

-- 订单表
CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER REFERENCES users(id),
    payment_id      TEXT,                         -- 第三方支付订单号
    amount          REAL NOT NULL,
    currency        TEXT DEFAULT 'CNY',
    status          TEXT DEFAULT 'pending',       -- pending/paid/refunded
    product_type    TEXT DEFAULT 'usb',            -- usb/download/subscription
    shipping_address TEXT,                        -- 快递地址（U盘版）
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at         DATETIME
);

-- 下载记录表
CREATE TABLE downloads (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER REFERENCES users(id),
    version         TEXT NOT NULL,
    downloaded_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address      TEXT
);
```

---

## 五、API设计

### 5.1 公开API（用户端）

```
POST /api/v1/orders
  功能：提交订单
  请求：{ spell_origin, email?, payment_id, product_type, shipping_address? }
  响应：{ order_id, status: 'paid'|'pending' }
  触发：Webhook接收支付成功通知后自动处理

GET /api/v1/download/{token}
  功能：获取下载链接
  请求：Header: X-Activation-Key
  响应：{ download_url, expires_at }
  说明：下载包在服务端动态植入Incantation

POST /api/v1/verify
  功能：快速校验Incantation（不涉及HIPPO本地）
  请求：{ incantation, spell_origin }
  响应：{ valid: bool, expires_at, features: [] }

GET /api/v1/status/{token}
  功能：查询授权状态
  响应：{ active: bool, expires_at, days_left }
```

### 5.2 管理API（鱼总专用）

```
POST /admin/api/keygen
  功能：生成Incantation（鱼总本地工具的API版，备用）
  请求：{ spell_origin, days, rune }
  响应：{ incantation, expires_at }
  安全：需要Admin Bearer Token

POST /admin/api/users
  功能：手动创建用户+Incantation
  请求：{ spell_origin, email?, days }
  响应：{ user_id, incantation }

GET /admin/api/users
  功能：列出所有用户
  查询：?status=active&page=1&limit=50
  响应：{ users: [], total, page }

PATCH /admin/api/activations/{id}/revoke
  功能：吊销Incantation
  请求：{ reason }
  响应：{ success: bool }

POST /admin/api/burn
  功能：U盘烧录（远程API版）
  请求：{ user_id, device_serial }
  响应：{ success: bool, burn_log }
  说明：需要云服务器能访问烧录工具（实际场景中U盘在鱼总手上，
        所以这个API主要是给管理后台展示记录用）
```

### 5.3 Webhook（支付回调）

```
POST /api/v1/webhooks/stripe          (Stripe支付)
POST /api/v1/webhooks/baidu_pay       (百度pay/国内支付)
POST /api/v1/webhooks/admin_notify     (管理员通知)

通用处理逻辑：
  1. 验证签名
  2. 查询订单
  3. 更新订单状态
  4. 生成/发送Incantation
  5. 发送邮件
```

---

## 六、密钥生成算法（v2详细版）

### 6.1 算法选择

```
HMAC-SHA256
- 优点：不可伪造、无需公私钥对、计算快
- 缺点：需要服务端持有Arcanum
- 适用场景：客户端验证（无Arcanum泄露风险）
```

### 6.2 Incantation生成流程

```
输入：
  spell_origin = "FishMaster2026"  # Spell-origin示例   # Spell-origin
  rune       = "HP2026"              # Rune
  expiry     = "2027-05-21"
  arcanum = "O3kQp9Vx2...（Base64编码的32字节）"

Step 1: 构造消息
  message = f"{spell_origin.lower()}|{rune}|{expiry}"
          = "fishmaster2026|HP2026|2027-05-21"  # Spell-origin|Rune|Expiry

Step 2: HMAC-SHA256签名
  import hmac, hashlib, base64
  signature_raw = hmac.new(
      key=base64.b64decode(arcanum),
      msg=message.encode('utf-8'),
      digestmod=hashlib.sha256
  ).digest()

Step 3: 取前16字节 + Base32编码
  signature_b32 = base64.b32encode(signature_raw[:16]).decode().rstrip('=')
              = "JBSWY3DPEHPK3PXP"

Step 4: 格式化
  incantation = token[:4].upper() + "-" + signature_b32 + "-" + expiry[-4:]
              = "FISH-JBSWY3DPEHPK3PXP-0521"

Step 5: 存入DB
  INSERT INTO activations (user_id, incantation, expires_at, rune)
  VALUES (123, 'FISH-JBSWY3DPEHPK3PXP-0521', '2027-05-21', 'HP2026')
```

### 6.3 Incantation校验流程（HIPPO本地）

```
输入：
  .hippo_license文件内容
  内置的 rune = "HP2026"（代码中常量，公开）
  内置的 鱼总公钥相关信息（可选：存放用于比较的签名样本）

Step 1: 读取.hippo_license
  {
    "token_hash": "a1b2c3d4...",  // SHA256(token.lower())
    "incantation": "FISH-JBSWY3DPEHPK3PXP-0521",
    "expires_at": "2027-05-21",
    "features": ["read", "write", "organize"]
  }

Step 2: 提取各部分
  token_part = "FISH"
  sig_part = "JBSWY3DPEHPK3PXP"
  expiry_part = "0521" → 完整到期日需结合注册时间推算

Step 3: 重建消息（需要本地有token原文来计算哈希）
  // 本地只存了token_hash，需要用户提供token来验证
  // 流程：启动时让用户输入Spell-origin → 计算SHA256 → 与存储的hash比对
  // 比对成功后：
  message = f"{user_token.lower()}|{rune}|{full_expiry}"

Step 4: 服务端签名验证（需要Arcanum，在服务端做）
  // 方案A：本地验证（推荐）
  // .hippo_license中直接存一个"校验值"——用Arcanum对固定字符串的签名
  // 本地校验时用预存公钥验证这个签名（不解密，只比较）
  // 
  // 方案B：服务端API验证（简单但依赖网络）
  // POST /api/v1/verify { incantation, spell_origin }
  // 服务端返回 { valid: true }

  推荐方案A+B混合：
  - 日常快速校验：本地校验"校验值"（<1ms）
  - 启动完整校验：比对token_hash + 验证Incantation格式 + 检查到期日
  - 疑难杂症：调用服务端API
```

### 6.4 本地快速校验（<100ms，纯本地）

```python
# license.py 核心校验逻辑
import hashlib, hmac, base64, json
from datetime import date

LICENSE_FILE = Path(__file__).parent.parent / "license" / ".hippo_license"
RUNE = "HP2026"  # Rune（符文标记）
BUILTIN_CHECK_SIG = "JBSWY3DPXXXXX..."  # 预存的校验签名

def verify_signature(message: str, sig: str) -> bool:
    """用预存公钥验证HMAC签名（本地完成，不需要Arcanum）"""
    expected = hmac.new(
        BUILTIN_CHECK_SIG.encode(),  # 用Incantation本身做HMAC密钥
        message.encode(),
        hashlib.sha256
    ).digest()[:16]
    return hmac.compare_digest(expected, base64.b32decode(sig + "===="))

def is_activated(token: str) -> bool:
    if not LICENSE_FILE.exists():
        return False

    data = json.loads(LICENSE_FILE.read_text())

    # 1. token哈希验证
    if data["token_hash"] != hashlib.sha256(token.lower().encode()).hexdigest():
        return False

    # 2. 到期检查
    expires = date.fromisoformat(data["expires_at"])
    if date.today() > expires:
        return False

    # 3. 签名验证（核心防伪）
    message = f"{token.lower()}|{RUNE}|{data['expires_at']}"
    sig = data["incantation"].split("-")[1]
    if not verify_signature(message, sig):
        return False

    return True
```

---

## 七、U盘烧录工具（burn_usb.py 详细设计）

### 7.1 使用场景

```
鱼总收到U盘订单 → 运行burn_usb.py → 程序自动完成所有步骤 → 打包发货
```

### 7.2 命令行接口

```bash
python3 burn_usb.py \
  --spell-origin "FishMaster2026"  # Spell-origin示例 \
  --days 365 \
  --device /dev/sdX \
  --output ./shipped/

# 参数说明
--spell-origin      用户Spell-origin（必须）
--days       授权天数（默认365）
--device     U盘设备路径（默认自动检测第一个可移动磁盘）
--output     烧录完成后的日志输出目录
--dry-run    模拟运行（不实际写入U盘）
--format     是否格式化U盘（默认提示确认）
```

### 7.3 内部流程

```
1. [准备] 加载arcanum.key（从本地文件或环境变量）
2. [检测] 列出可用移动磁盘，供用户选择
3. [确认] 显示目标U盘信息（容量、当前文件系统），要求确认
4. [格式化] （可选）FAT32/NTFS格式化
5. [生成] 用keygen.py生成Incantation
6. [复制] 将程序目录复制到U盘根目录
7. [写入] 创建license/.hippo_license，写入Incantation
8. [验证] 读取并校验写入的内容
9. [日志] 记录到output/目录（shipment_YYYYMMDD_HHMMSS.log）
10. [完成] 显示摘要，等待打包发货
```

### 7.4 防止误操作的安全措施

```python
# 只允许写入到明确的 removable 设备
def is_safe_device(device_path: str) -> bool:
    # 1. 必须是 /dev/sd* 格式
    if not re.match(r'/dev/sd[a-z]$', device_path):
        return False
    # 2. 必须是 removable 设备
    if not Path(f"/sys/block/{Path(device_path).name}/removable"):
        return False
    # 3. removable标志必须为1
    with open(f"/sys/block/{Path(device_path).name}/removable") as f:
        if f.read().strip() != "1":
            return False
    # 4. 不能是系统盘（检查 /dev/nvme /dev/sda 等）
    return True
```

---

## 八、网站与自动化

### 8.1 前端页面结构

```
gabe-luv-nancy.online
│
├── index.html          首页/落地页
├── register.html       注册页（Spell-origin申请）
├── pricing.html        定价页
├── download.html       下载页（激活后可见）
├── help.html           帮助文档
│
├── /api/...            （后端路由）
```

### 8.2 注册页面字段

```html
<form id="register-form">
  <!-- Spell-origin（必填）-->
  <input type="text" name="token" 
         placeholder="设定Spell-origin（8-20位，字母+数字）"
         pattern="[a-zA-Z0-9]{8,20}"
         required>

  <!-- 邮箱（选填，仅推广用）-->
  <input type="email" name="email"
         placeholder="邮箱（选填，用于接收下载链接）">

  <!-- 产品类型（U盘版需要地址）-->
  <select name="product_type">
    <option value="usb">U盘版（需快递，+快递费）</option>
    <option value="download">下载版（即时下载）</option>
  </select>

  <!-- 快递地址（U盘版显示）-->
  <textarea name="shipping_address"
            placeholder="收货地址（U盘版必填）"></textarea>

  <!-- 支付按钮 -->
  <button type="submit">前往支付 $XX</button>
</form>
```

### 8.3 付费集成选项

| 方案         | 接入难度      | 手续费        | 适用场景       |
| ---------- | --------- | ---------- | ---------- |
| Stripe     | 低（API成熟）  | 2.9%+$0.30 | 美元结算，海外用户  |
| 支付宝/微信     | 中（需要企业资质） | 0.6%       | 国内用户       |
| 百度开发者支付    | 低（个人可用）   | 约1%        | 国内，测试阶段    |
| BuyVM等加密货币 | 无手续费      | 0          | 全域，匿名购买    |
| 手动转账       | 无         | 0          | 高价值用户，信任优先 |

**推荐v1.0策略：**

- Stripe（海外）+ 手动转账/加密货币（高隐私用户）
- 国内先用百度pay或微信个人收款码（规避企业资质问题）

### 8.4 自动化触发器

```python
# webhook_handler.py

@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers["stripe-signature"]

    # 验证Stripe签名
    event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session["metadata"]

        # 自动化处理
        if metadata["product_type"] == "download":
            # 发送下载链接
            await send_download_email(
                to=metadata["email"],
                token=metadata["token"],
                download_url=generate_signed_url(metadata["token"])
            )

        elif metadata["product_type"] == "usb":
            # 通知鱼总准备发货
            await notify_admin_usb_order(
                token=metadata["token"],
                shipping_address=metadata["shipping_address"],
                days=int(metadata["days"])
            )

    return {"received": True}
```

### 8.5 邮件通知（自动化）

```python
# 使用Resend/SendGrid/QQ企业邮箱

EMAIL_TEMPLATES = {
    "download_ready": """
    主题：🦛 Hippocampus 下载就绪

    你的Hippocampus已准备就绪！

    下载地址（30分钟内有效）：
    https://gabe-luv-nancy.online/download/{token}

    Incantation：{incantation}
    到期日：{expires_at}

    下载后解压，双击 Hippocampus 即可使用。
    """,

    "usb_ready": """
    主题：🦛 Hippocampus U盘正在准备发货

    你的U盘正在准备中，预计3天内发货。

    收件地址：{shipping_address}
    Incantation：{incantation}
    到期日：{expires_at}

    收货后双击 Hippocampus 即可使用。
    """,

    "expiry_reminder": """
    主题：⚠️ Hippocampus 授权即将到期

    你的Hippocampus授权将于 {days_left} 天后到期。

    如需续费，请联系鱼总。
    """
}
```

---

## 九、多端关联机制

### 9.1 物理距离带来的挑战

```
问题：
  - U盘版：鱼总在A地烧录 → 发快递到B地用户（物理隔阂）
  - 下载版：云服务器生成Incantation → 用户自行下载（数字隔阂）
  - 如何保证Incantation在烧录/下载时仍有效？
```

### 9.2 解决方案：Incantation预生成+Spell-origin哈希关联

```
方案设计：

1. 用户提交订单时：
   - token + token_hash 存入DB
   - Incantation NOT YET 生成（等支付确认）

2. 支付确认后：
   - 生成Incantation
   - U盘版：烧录时写入（Incantation实时生成）
   - 下载版：Incantation写入程序包 → 生成唯一下载链接

3. 关联机制：
   - 每个用户的唯一标识：SHA256(token.lower())
   - Incantation = token_prefix + HMAC_sig + expiry_suffix
   - 无法从Incantation反推token，但可以正向验证
```

### 9.3 远程U盘烧录（如果鱼总在外）

```
场景：鱼总不在实验室，U盘需要远程烧录

方案A：邮寄空白U盘
  - 用户下单 → 鱼总发空白U盘给用户
  - 用户收到 → 插上电脑 → 访问管理页面 → 远程执行burn脚本
  - 技术：云服务器API调用 → 触发用户本地agent → burn_usb.py运行
  - 风险：agent安全问题

方案B：快递已有U盘
  - 鱼总在实验室时批量烧录 → 快递发货
  - 这是最简单可靠的方案

方案C：Download Only
  - 不做物理U盘烧录
  - 全部走下载渠道
  - 用户自己安装到自己的U盘
  - 问题：如何防止传播Incantation？
  - 解决：machine_id绑定（可选功能，二期）

推荐v1.0：方案B为主，下载版为辅。
```

---

## 十、安全设计

### 10.1 密钥安全

| 密钥             | 存储位置       | 风险    | 防护           |
| -------------- | ---------- | ----- | ------------ |
| arcanum.key     | 鱼总本地电脑     | 丢失/泄露 | 离线备份，多重保护    |
| incantation | 用户磁盘+服务器DB | 泄露    | HMAC不可伪造     |
| token_hash     | 服务器DB      | 泄露    | SHA256单向，不可逆 |

### 10.2 防破解层级

```
Level 1: 基础校验（启动时）
  - .hippo_license存在性
  - token_hash匹配
  - expires_at未过期
  时间：<1ms

Level 2: 签名校验（操作前）
  - HMAC签名验证（用Incantation本身作为密钥的HMAC验证）
  时间：<5ms

Level 3: 服务端实时校验（可选）
  - POST /api/v1/verify
  时间：<100ms，依赖网络

Level 4: machine_id绑定（二期可选）
  - 硬件指纹绑定
  - 换电脑需重新激活
```

### 10.3 防共享策略

```
问题：一个Incantation多人使用

方案A：machine_id绑定
  - 首次激活记录硬件指纹
  - 后续激活时比对，不一致则警告
  - 优点：有效防共享
  - 缺点：换电脑麻烦

方案B：在线校验（需要网络）
  - 每次使用调用服务端API
  - 无网络时只能读取，不能写入
  - 优点：实时控制
  - 缺点：依赖网络

v1.0建议：不绑定，用"适度防破解"策略
  - 低价产品+低共享率 → 没必要做高强度绑定
  - 后续根据数据调整
```

---

## 十一、实施计划

### Phase 1：核心授权引擎（立即可做）

```
目标：HIPPO本地授权校验跑通
文件：lib/license.py

交付物：
  ✅ license.py 校验引擎
  ✅ .hippo_license 文件格式
  ✅ keygen.py 鱼总密钥生成工具
  ✅ burn_usb.py U盘烧录工具

优先级：P0
时间：1-2天
```

### Phase 2：云端基础设施（次优先）

```
目标：网站+API跑起来，公开访问
文件：cloud/ 目录

交付物：
  ✅ Nginx/Caddy 配置
  ✅ FastAPI REST API
  ✅ SQLite 数据库 + migrations
  ✅ 静态网站（注册、定价、下载）
  ✅ 支付Webhook接入（Stripe测试模式）
  ✅ 邮件发送（Resend/SendGrid）

优先级：P1
时间：3-5天
```

### Phase 3：分发自动化

```
目标：付费→Incantation生成→下载分发 全自动

交付物：
  ✅ 付费成功 → 自动发邮件
  ✅ 下载版：动态打包+唯一下载链接
  ✅ U盘版：管理后台订单列表
  ✅ 到期提醒邮件Cron

优先级：P1
时间：2-3天
```

### Phase 4：U盘版完整交付

```
目标：U盘到手可烧录发货

交付物：
  ✅ 物理U盘准备（鱼总操作）
  ✅ burn_usb.py 在鱼总电脑上运行
  ✅ 快递流程

优先级：P1
时间：鱼总准备好U盘后
```

---

## 十二、待鱼总确认事项

### 12.1 关键决策

| #   | 问题                     | 选项                              | 建议                   |
| --- | ---------------------- | ------------------------------- | -------------------- |
| 1   | **云服务器**                 | 腾讯云轻量应用服务器                    | ✅ 已确定               |
| 2   | **域名**                 | gabe-luv-nancy.online（已备案）           | ✅ 已确定               |
| 3   | **支付接入**               | Stripe+个人收款码                    | Stripe(海外)+百度pay(国内) |
| 4   | **arcanum.key存储**       | 本地文件/密码管理器                      | 本地加密文件+离线备份          |
| 5   | **v1.0是否绑定machine_id** | 是/否                             | 否，降低门槛               |
| 6   | **是否做下载版**             | 是/否                             | 是，下载版无物流成本           |
| 7   | **ICP备案**                  | 已备案（gabe-luv-nancy.online）       | ✅ 已完成               |
| 8   | **Rune用什么**       | HP2026（可每年换，开启新纪元）                       | HP2026（可每年换，开启新纪元）         |

### 12.2 鱼总需提供的资料

```
1. 云服务器：✅ 已有腾讯云轻量应用服务器
2. 域名：✅ gabe-luv-nancy.online（已备案+SSL）
3. 邮箱：用于管理后台和发送通知
4. 支付收款：Stripe账户/国内收款二维码
5. 快递：用什么快递？发货频率预估？
```

---

## 附录A：文件结构

```
HIPPO/
├── cloud/                          # 云服务器端（网站+API）
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI入口
│   │   ├── routers/
│   │   │   ├── users.py
│   │   │   ├── orders.py
│   │   │   ├── activations.py
│   │   │   ├── webhooks.py
│   │   │   └── admin.py
│   │   ├── models/                 # Pydantic models
│   │   ├── db/                     # SQLite/DB连接
│   │   └── templates/              # 邮件模板
│   ├── static/                     # 静态网站
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── pricing.html
│   │   └── download.html
│   └── scripts/
│       ├── init_db.py
│       └── seed_admin.py
│
├── tools/                          # 鱼总专用工具（不离线分发）
│   ├── keygen.py                   # Incantation生成器
│   ├── burn_usb.py                 # U盘烧录工具
│   ├── arcanum.key                  # ArcanumArcanum（绝不离线）
│   └── requirements-tools.txt
│
├── hippocampus/                    # 产品代码（需植入授权）
│   ├── lib/
│   │   ├── license.py              # Grimoire授权校验引擎
│   │   ├── scanner.py
│   │   └── ...
│   ├── gui/
│   │   ├── app.py
│   │   ├── utils/
│   │   └── main.py
│   ├── license/                    # 授权目录
│   │   └── .hippo_license         # 用户Grimoire（烧录时写入）
│   ├── Hippocampus                # Linux入口
│   ├── Hippocampus.bat            # Windows入口
│   └── ...
│
└── PROJECTHOW/
    └── AUTH_SYSTEM_v2_FULL.md       # 本文档
```

---

## 附录B：快速参考卡片

```bash
# ========== 鱼总日常操作 ==========

# 生成Incantation
python3 keygen.py --spell-origin "FishMaster2026"  # Spell-origin示例 --days 365
# 输出: FISH-JBSWY3DPEHPK3PXP-0521

# 烧录U盘
python3 burn_usb.py --spell-origin "FishMaster2026"  # Spell-origin示例 --days 365 --device /dev/sdX

# 批量生成（for分销商）
python3 batch_generate.py --csv users.csv --output ./keys/

# ========== API快速测试 ==========

# 验证Incantation
curl -X POST https://gabe-luv-nancy.online/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "FishMaster2026"  # Spell-origin示例, "incantation": "FISH-JBSWY3DPEHPK3PXP-0521"}'

# 查询状态
curl https://gabe-luv-nancy.online/api/v1/status/FishMaster2026

# ========== 用户端体验 ==========

# U盘用户：插U盘 → 双击Hippocampus → 直接用
# 下载用户：收到链接 → 下载 → 解压 → 双击Hippocampus → 直接用
# 两种用户都不需要手动输入Incantation（已植入）
```
