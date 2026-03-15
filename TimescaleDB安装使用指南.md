# TimescaleDB 免费开源版安装使用指南

## 一、TimescaleDB 简介

### 1.1 什么是 TimescaleDB

TimescaleDB 是 PostgreSQL 的时序数据库扩展，专为高性能时序数据场景设计：

| 特性 | 说明 |
|------|------|
| **时序优化** | 专为物联网、金融、监控等时序数据场景优化 |
| **自动分区** | 自动将数据按时间分区，提升查询性能 |
| **完整 SQL** | 100% 兼容 PostgreSQL SQL 语法 |
| **开源免费** | Apache 2 许可证，社区版完全免费 |
| **插件生态** | 支持 Prometheus、Telegraf 等数据源 |

### 1.2 TimescaleDB vs PostgreSQL 对比

| 特性 | PostgreSQL | TimescaleDB |
|------|------------|-------------|
| 时序写入 | ~10K 行/秒 | ~100K+ 行/秒 |
| 压缩率 | 无 | 90%+ 压缩 |
| 自动分区 | 需手动 | 自动 |
| 时序函数 | 无 | 丰富内置函数 |
| 许可证 | PostgreSQL | Apache 2 |

### 1.3 适用场景

- **物联网 (IoT)**：传感器数据采集
- **金融行情**：股票、加密货币 tick 数据
- **应用监控**：APM、Metrics
- **日志分析**：ELK 替代方案
- **用户行为分析**：App/Web 埋点数据

---

## 二、Docker 安装方案（推荐）

### 2.1 前置要求

```bash
# 检查 Docker 是否安装
docker --version

# 检查 Docker Compose 是否安装
docker compose version
```

### 2.2 快速启动（单节点）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: timescaledb
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: timescale_db
    ports:
      - "5432:5432"
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d timescale_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  timescaledb_data:
```

启动服务：

```bash
# 启动
docker compose up -d

# 查看日志
docker compose logs -f timescaledb

# 停止
docker compose down
```

### 2.3 生产级配置（推荐）

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: timescaledb
    restart: unless-stopped
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD:-your_secure_password}
      POSTGRES_DB: timescale_db
      POSTGRES_MAX_CONNECTIONS: 200
    ports:
      - "5432:5432"
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
      - ./backups:/backups
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "work_mem=16MB"
      - "-c"
      - "maintenance_work_mem=128MB"
      - "-c"
      - "timescaledb.max_background_workers=8"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d timescale_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  # 可选：Adminer Web管理界面
  adminer:
    image: adminer
    container_name: timescaledb-adminer
    restart: unless-stopped
    ports:
      - "8080:8080"

volumes:
  timescaledb_data:
```

### 2.4 高可用配置（可选）

```yaml
version: '3.8'

services:
  timescaledb-primary:
    image: timescale/timescaledb:latest-pg16
    container_name: timescaledb-primary
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: timescale_db
    ports:
      - "5432:5432"
    volumes:
      - primary_data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "wal_level=replica"
      - "-c"
      - "max_wal_senders=3"
      - "-c"
      - "max_replication_slots=3"

  timescaledb-replica:
    image: timescale/timescaledb:latest-pg16
    container_name: timescaledb-replica
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: timescale_db
    ports:
      - "5433:5432"
    volumes:
      - replica_data:/var/lib/postgresql/data
    command: postgres -c primary_conninfo=host=timescaledb-primary port=5432 user=admin password=your_password
    depends_on:
      timescaledb-primary:
        condition: service_healthy

volumes:
  primary_data:
  replica_data:
```

---

## 三、本机安装方案（不使用 Docker）

### 3.1 Ubuntu/Debian 安装

```bash
# 1. 添加 TimescaleDB 仓库
echo "deb https://package.timescale.com/$(. /etc/os-release; echo $VERSION_ID)/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://package.timescale.com/timescale.key | sudo apt-key add -
sudo apt-get update

# 2. 安装 TimescaleDB
sudo apt-get install timescaledb-2-postgresql-16

# 3. 配置 PostgreSQL
sudo timescaledb_tune.sh

# 4. 重启 PostgreSQL
sudo systemctl restart postgresql
```

### 3.2 CentOS/RHEL 安装

```bash
# 1. 添加仓库
sudo tee /etc/yum.repos.d/timescale.repo << EOF
[timescale_timescaledb]
name=TimescaleDB
baseurl=https://package.timescale.com/repo/rpm\$basearch/\$releasever
enabled=1
gpgcheck=1
gpgkey=https://package.timescale.com/timescale.key
EOF

# 2. 安装
sudo yum install timescaledb-2-postgresql-16

# 3. 配置
sudo timescaledb_tune.sh -conf-path /etc/postgresql/16/main/postgresql.conf

# 4. 重启
sudo systemctl restart postgresql
```

### 3.3 macOS 安装

```bash
# 使用 Homebrew
brew update
brew install timescaledb

# 启动 PostgreSQL
brew services start postgresql@16

# 配置
sudo timescaledb_tune.sh
```

---

## 四、初始化配置

### 4.1 启用 TimescaleDB 扩展

```sql
-- 连接到数据库
psql -h localhost -U admin -d timescale_db

-- 创建 TimescaleDB 扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### 4.2 性能优化参数

在 PostgreSQL 配置文件中添加（或通过 Docker command 设置）：

```ini
# 共享内存
shared_buffers = 256MB  # 建议 25% 可用内存

# 工作内存
work_mem = 16MB

# 维护内存
maintenance_work_mem = 128MB

# TimescaleDB 后台工作进程
timescaledb.max_background_workers = 8

# WAL 压缩
wal_compression = on

# 自动清理
autovacuum = on
```

---

## 五、基本使用

### 5.1 创建超表（Hypertable）

```sql
-- 创建普通表
CREATE TABLE conditions (
    time        TIMESTAMPTZ       NOT NULL,
    device_id   TEXT              NOT NULL,
    temperature DOUBLE PRECISION  NULL,
    humidity    DOUBLE PRECISION NULL
);

-- 转换为超表
SELECT create_hypertable('conditions', 'time');

-- 创建索引
CREATE INDEX ON conditions (device_id, time DESC);
```

### 5.2 压缩配置（节省 90%+ 存储）

```sql
-- 启用压缩
ALTER TABLE conditions SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id'
);

-- 添加压缩策略（7天后压缩）
SELECT add_compression_policy('conditions', INTERVAL '7 days');
```

### 5.3 数据写入

```sql
-- 插入数据
INSERT INTO conditions VALUES 
    (NOW(), 'sensor1', 22.5, 60.0),
    (NOW(), 'sensor2', 23.1, 58.5);
```

### 5.4 时序查询示例

```sql
-- 最近 1 小时的平均温度
SELECT device_id, AVG(temperature) 
FROM conditions 
WHERE time > NOW() - INTERVAL '1 hour' 
GROUP BY device_id;

-- 降采样：按 5 分钟聚合
SELECT time_bucket('5 minutes', time) AS bucket,
       device_id,
       AVG(temperature) AS avg_temp
FROM conditions
WHERE time > NOW() - INTERVAL '1 day'
GROUP BY bucket, device_id
ORDER BY bucket DESC;

-- 实时聚合（连续聚合）
CREATE MATERIALIZED VIEW hourly_avg_temp
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS hour,
       device_id,
       AVG(temperature) AS avg_temp
FROM conditions
GROUP BY hour, device_id;

-- 添加实时聚合刷新策略
SELECT add_continuous_aggregate_policy('hourly_avg_temp',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '5 minutes');
```

---

## 六、常用管理命令

### 6.1 Docker 管理

```bash
# 查看状态
docker compose ps

# 查看资源使用
docker stats timescaledb

# 进入容器
docker exec -it timescaledb psql -U admin -d timescale_db

# 备份数据
docker exec timescaledb pg_dump -U admin timescale_db > backup.sql

# 恢复数据
docker exec -i timescaledb psql -U admin timescale_db < backup.sql
```

### 6.2 监控查询

```sql
-- 查看超表信息
SELECT * FROM timescaledb_information.hypertables;

-- 查看压缩统计
SELECT * FROM timescaledb_information.compression_stats;

-- 查看Chunks信息
SELECT * FROM timescaledb_information.chunks;
```

---

## 七、连接方式

### 7.1 命令行连接

```bash
# 本地连接
psql -h localhost -U admin -d timescale_db

# Docker 内部连接
docker exec -it timescaledb psql -U admin -d timescale_db
```

### 7.2 应用程序连接

```python
# Python 示例 (psycopg2)
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="timescale_db",
    user="admin",
    password="your_password"
)
```

```javascript
// Node.js 示例 (pg)
const { Pool } = require('pg');
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'timescale_db',
  user: 'admin',
  password: 'your_password'
});
```

---

## 八、数据迁移（从 PostgreSQL）

### 8.1 从普通表迁移

```sql
-- 将普通表转换为超表
SELECT create_hypertable('existing_table', 'time_column');

-- 或使用 migrate 命令行工具
timescaledb_migrate -o postgresql://admin:password@localhost:5432/old_db
```

---

## 九、备份与恢复

### 9.1 物理备份

```bash
# 停止写入
docker compose stop timescaledb

# 备份数据目录
docker compose rm -v timescaledb
docker volume rm timescaledb_timescaledb_data

# 恢复时重新创建容器
docker compose up -d
```

### 9.2 SQL 逻辑备份

```bash
# 备份
docker exec timescaledb pg_dump -U admin timescale_db > timescale_backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i timescaledb psql -U admin timescale_db < timescale_backup_20240310.sql
```

---

## 十、常见问题

### 10.1 Q: TimescaleDB 社区版免费吗？

> A: 是的，Apache 2.0 许可证，完全免费。商业功能（如数据分层到对象存储）需要 TimescaleCloud。

### 10.2 Q: 如何选择版本？

> A: 生产环境建议使用 PostgreSQL 15 或 16 配合对应 TimescaleDB 版本。

### 10.3 Q: Docker 性能差怎么办？

> A: 
> 1. 增加 shared_buffers
> 2. 使用主机网络：`network_mode: host`
> 3. 挂载内存盘：`tmpfs: /var/lib/postgresql/data`

### 10.4 Q: 如何升级版本？

> A:
> ```bash
> # 停止容器
> docker compose down
> 
> # 更新镜像
> docker compose pull
> 
> # 启动（会自动迁移）
> docker compose up -d
> ```

---

## 附录：快速命令速查

```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 查看日志
docker compose logs -f

# 进入数据库
docker exec -it timescaledb psql -U admin -d timescale_db

# 查看状态
docker compose ps
```

---

*文档创建时间：2026-03-10*
*参考资料：https://docs.timescale.com*
