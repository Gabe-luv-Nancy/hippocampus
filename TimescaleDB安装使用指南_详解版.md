# TimescaleDB 完整安装使用指南（详解版）

## 一、核心概念解释

### 1.1 什么是 TimescaleDB？

**一句话解释**：TimescaleDB = PostgreSQL + 时序数据优化插件

| 概念 | 解释 |
|------|------|
| **PostgreSQL** | 一个功能强大的开源关系型数据库 |
| **时序数据** | 按时间顺序产生的数据（如传感器读数、股票价格、监控指标） |
| **TimescaleDB插件** | 安装在PostgreSQL上的扩展，，专门优化时序数据读写 |

**为什么需要它？**
- 普通数据库写入时序数据：约 1,000 条/秒
- TimescaleDB写入时序数据：约 100,000+ 条/秒（快100倍）

---

### 1.2 Docker 是什么？为什么要用 Docker 安装？

**Docker = 轻量级虚拟机**

| 对比项 | 传统安装 | Docker 安装 |
|--------|----------|-------------|
| 安装复杂度 | 高（需配置系统依赖） | 低（一条命令） |
| 卸载难度 | 复杂，可能残留 | 一条命令干净删除 |
| 版本切换 | 麻烦 | 改配置重启即可 |
| **适合人群** | 运维熟练者 | 开发者/快速测试 |

**Docker 最小理解**：
- 想象成"标准化集装箱"
- 你的TimescaleDB"集装箱"在任何电脑都能运行
- 不需要关心"集装箱"里的具体安装过程

---

## 二、最小可行方案（推荐 90% 用户）

### 2.1 方案选择

**推荐使用 Docker 单节点方案**，理由：
- ✅ 安装简单（3步完成）
- ✅ 不需要额外安装 PostgreSQL
- ✅ 一键启动/停止
- ✅ 数据可持久保存

### 2.2 最小化安装步骤

#### 步骤 1：检查 Docker 是否已安装

```bash
docker --version
```

**预期输出**：
```
Docker version 24.0.0, build xxxxx
```

**如果没安装**（Windows/Mac）：
1. 下载 Docker Desktop：https://www.docker.com/products/docker-desktop/
2. 安装后启动

**如果没安装**（Linux Ubuntu）：
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

---

#### 步骤 2：创建数据存储目录

```bash
# 在当前用户目录下创建timescale数据文件夹
mkdir -p ~/timescale_data
```

**解释**：这个文件夹用来存放数据库里的数据。
- 不创建 = 容器删除后数据丢失
- 创建了 = 容器删除后数据还在

---

#### 步骤 3：启动 TimescaleDB 容器

```bash
docker run -d \
  --name timescaledb \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=timescaledb \
  -p 5432:5432 \
  -v ~/timescale_data:/var/lib/postgresql/data \
  timescale/timescaledb:latest-pg16
```

**逐行解释**：

| 代码部分 | 含义 |
|---------|------|
| `docker run -d` | 后台运行容器 |
| `--name timescaledb` | 给容器起个名字，方便管理 |
| `-e POSTGRES_USER=admin` | 设置数据库用户名 = admin |
| `-e POSTGRES_PASSWORD=admin123` | 设置密码 = admin123（生产环境请改强密码）|
| `-e POSTGRES_DB=timescaledb` | 创建数据库名 = timescaledb |
| `-p 5432:5432` | 把容器内的5432端口映射到电脑的5432端口 |
| `-v ~/timescale_data:/var/lib/postgresql/data` | 把数据存在本地文件夹 |
| `timescale/timescaledb:latest-pg16` | 使用TimescaleDB镜像（PostgreSQL 16版本）|

---

#### 步骤 4：验证安装成功

```bash
# 检查容器是否在运行
docker ps

# 应该看到类似输出：
# CONTAINER ID   IMAGE                    STATUS          PORTS
# abc123        timescale/timescaledb    Up 2 minutes   0.0.0.0:5432->5432/tcp
```

---

## 三、各操作详解

### 3.1 常用操作命令

#### 启动数据库
```bash
# 如果容器已停止，重新启动
docker start timescaledb
```

#### 停止数据库
```bash
docker stop timescaledb
```

#### 查看日志
```bash
docker logs timescaledb

# 实时查看日志
docker logs -f timescaledb
```

#### 进入数据库（类似打开数据库客户端）
```bash
docker exec -it timescaledb psql -U admin -d timescale_db
```

**进入后会看到**：
```
psql (16.x)
Type "help" for help.

timescale_db=#
```

输入 `\q` 可退出。

---

### 3.2 连接方式汇总

| 场景 | 连接参数 |
|------|----------|
| Docker内部连接 | `docker exec -it timescaledb psql -U admin -d timescale_db` |
| 本地应用连接 | `host=localhost, port=5432, user=admin, password=admin123, database=timescale_db` |
| 远程连接 | 把localhost换成服务器IP |

---

## 四、初始化配置（可选但推荐）

### 4.1 启用 TimescaleDB 扩展

在数据库中执行：

```sql
-- 连接后执行这句
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

**解释**：告诉PostgreSQL加载TimescaleDB的优化功能

### 4.2 创建一个时序表

```sql
-- 创建测试表
CREATE TABLE sensor_data (
    time        TIMESTAMPTZ       NOT NULL,
    device_id   TEXT              NOT NULL,
    temperature DOUBLE PRECISION  NULL,
    humidity    DOUBLE PRECISION NULL
);

-- 转换为超表（TimescaleDB的核心优化）
SELECT create_hypertable('sensor_data', 'time');

-- 插入测试数据
INSERT INTO sensor_data VALUES 
    (NOW(), 'device_001', 25.3, 60.5),
    (NOW(), 'device_002', 26.1, 58.2);
```

---

## 五、本机安装方案（不推荐用于测试）

**只有以下情况才考虑本机安装**：
- 需要极致性能（Docker有性能损耗）
- 需要长期运行且熟悉Linux
- 容器技术不可用

### 5.1 Ubuntu 本机安装

#### 步骤1：添加TimescaleDB官方仓库

```bash
# 1. 添加仓库
echo "deb https://package.timescale.com/$(. /etc/os-release; echo $VERSION_ID)/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list

# 2. 添加密钥
wget --quiet -O - https://package.timescale.com/timescale.key | sudo apt-key add -

# 3. 更新
sudo apt update
```

**解释**：
- 告诉系统从哪里下载TimescaleDB
- 类似手机应用商店添加应用源

#### 步骤2：安装

```bash
# 安装TimescaleDB
sudo apt install timescaledb-2-postgresql-16
```

**解释**：从刚才添加的仓库下载安装

#### 步骤3：优化配置

```bash
# 自动配置（回答Yes）
sudo timescaledb_tune.sh
```

**解释**：自动调整PostgreSQL配置参数，使其性能最优

#### 步骤4：重启服务

```bash
sudo systemctl restart postgresql
```

---

## 六、卸载/

清理### 6.1 Docker 方案卸载

```bash
# 1. 停止并删除容器
docker stop timescaledb
docker rm timescaledb

# 2. 删除数据（可选）
rm -rf ~/timescale_data
```

### 6.2 本机安装卸载（Ubuntu）

```bash
sudo apt remove timescaledb-2-postgresql-16
sudo rm /etc/apt/sources.list.d/timescaledb.list
```

---

## 七、故障排查

### 7.1 连接失败

| 检查项 | 命令 |
|--------|------|
| 容器是否运行 | `docker ps` |
| 端口是否冲突 | `netstat -tlnp \| grep 5432` |
| 日志查看 | `docker logs timescaledb` |

### 7.2 忘记密码

```bash
# 重新创建容器（数据会丢失！）
docker rm -f timescaledb
# 重新运行安装命令（用新密码）
```

---

## 八、最小可行方案总结

**只需要3条命令**：

```bash
# 1. 创建数据目录
mkdir -p ~/timescale_data

# 2. 启动数据库（把admin123改成你的密码）
docker run -d --name timescaledb \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=timescale_db \
  -p 5432:5432 \
  -v ~/timescale_data:/var/lib/postgresql/data \
  timescale/timescaledb:latest-pg16

# 3. 验证运行
docker ps
```

**验证连接**：
```bash
docker exec -it timescaledb psql -U admin -d timescale_db
```

看到 `timescale_db=#` 就成功了！

---

## 九、安全说明

| 项目 | 建议 |
|------|------|
| 密码 | 生产环境使用强密码，不要用admin123 |
| 端口 | 只在内网暴露，不要直接对公网 |
| 备份 | 定期备份 ~/timescale_data 目录 |
| 更新 | 关注TimescaleDB安全公告 |

---

*文档更新时间：2026-03-10*
