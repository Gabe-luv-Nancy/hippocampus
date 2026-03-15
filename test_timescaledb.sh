#!/bin/bash
# TimescaleDB 测试脚本

echo "=== TimescaleDB 自动化测试 ==="

# 测试1: 检查容器状态
echo ""
echo "[1] 检查容器状态..."
CONTAINER_STATUS=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker ps --filter 'name=timescaledb' --format '{{.Status}}'" 2>&1)
echo "容器状态: $CONTAINER_STATUS"

# 测试2: 检查数据库版本
echo ""
echo "[2] 测试数据库连接..."
VERSION=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker exec timescaledb psql -U admin -d timescaledb -t -c 'SELECT version();'" 2>&1 | head -1)
echo "数据库版本: $VERSION"

# 测试3: 创建测试数据库
echo ""
echo "[3] 创建测试数据库..."
DB_RESULT=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker exec timescaledb psql -U admin -d postgres -c 'CREATE DATABASE lott;'" 2>&1)
echo "数据库创建: $DB_RESULT"

# 测试4: 创建元数据表
echo ""
echo "[4] 创建元数据表..."
TABLE_SQL="CREATE TABLE IF NOT EXISTS data_metadata (id SERIAL PRIMARY KEY, data_hash TEXT NOT NULL UNIQUE, source_file TEXT, source_type TEXT DEFAULT 'json', level1 TEXT, level2 TEXT, level3 TEXT, level4 TEXT, timeframe TEXT NOT NULL, start_time TIMESTAMPTZ, end_time TIMESTAMPTZ, row_count BIGINT DEFAULT 0, null_count BIGINT DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());"
TABLE_RESULT=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker exec timescaledb psql -U admin -d lott -c '$TABLE_SQL'" 2>&1)
echo "表创建: $TABLE_RESULT"

# 测试5: 插入测试数据
echo ""
echo "[5] 插入测试数据..."
INSERT_SQL="INSERT INTO data_metadata (data_hash, source_file, level1, level2, level3, timeframe, row_count) VALUES ('test_hash_001', 'test.json', '159315.SZ', '黄金ETF', '收盘价', '1d', 100) ON CONFLICT (data_hash) DO NOTHING;"
INSERT_RESULT=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker exec timescaledb psql -U admin -d lott -c '$INSERT_SQL'" 2>&1)
echo "插入: $INSERT_RESULT"

# 测试6: 查询数据
echo ""
echo "[6] 查询数据..."
QUERY_RESULT=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "docker exec timescaledb psql -U admin -d lott -c 'SELECT * FROM data_metadata;'" 2>&1)
echo "$QUERY_RESULT"

echo ""
echo "=== 测试完成 ==="
