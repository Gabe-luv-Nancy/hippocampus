# SimNow 数据收集需求规格

## 执行时间
- 每天开盘前：8:55 自动启动
- 交易时段：持续收集

## 数据要求

### 1. 全量品种
- 所有可交易的期货合约
- 70+ 合约（含股指、国债、金属、能源、化工、农产品等）
- 需覆盖：IF, IC, IH, IM, T, TF, TS, TA, MA, PF, RU, FU, CU, AL, ZN, PB, SN, NI, AU, AG, RB, HC, I, J, JM, SR, CF, CS, C, M, Y, P, A, B, RM, O, ZC, AP, CJ, JR, LR, SM, RS, RM 等

### 2. 全量数据类型
必须收集的数据类型：
- [ ] 行情数据 (Quote) - 最新价、涨跌、持仓量、成交量等
- [ ] 持仓数据 (Position) - 多空持仓、持仓盈亏
- [ ] 成交记录 (Trade) - 成交明细
- [ ] 委托订单 (Order) - 委托状态
- [ ] 资金账户 (Account) - 账户权益、可用资金
- [ ] 合约信息 (Instrument) - 合约详情

### 3. 数据完整性检查
- [ ] 每条数据包含时间戳
- [ ] 合约代码不为空
- [ ] 数值字段有有效值
- [ ] 无重复数据

## 数据库结构

### SQLite 表设计
```sql
-- 行情数据
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY,
    instrument_code TEXT,      -- 合约代码
    timestamp INTEGER,         -- 时间戳
    last_price REAL,           -- 最新价
    volume INTEGER,            -- 成交量
    open_interest INTEGER,     -- 持仓量
    bid_price1 REAL,           -- 买价
    ask_price1 REAL,           -- 卖价
    bid_volume1 INTEGER,       -- 买量
    ask_volume1 INTEGER,       -- 卖量
    change REAL,               -- 涨跌
    change_pct REAL,           -- 涨跌幅
    open_price REAL,           -- 开盘价
    high_price REAL,           -- 最高价
    low_price REAL,            -- 最低价
    close_price REAL,          -- 收盘价
    pre_close REAL,            -- 昨收价
    pre_settle REAL,           -- 昨结算
    settle_price REAL,         -- 结算价
    pre_open_interest INTEGER, -- 昨持仓
    created_at INTEGER         -- 创建时间
);

-- 持仓数据
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    instrument_code TEXT,
    timestamp INTEGER,
    long_position INTEGER,     -- 多头持仓
    short_position INTEGER,    -- 空头持仓
    long_pnl REAL,             -- 多头盈亏
    short_pnl REAL,            -- 空头盈厄
    avg_long_price REAL,       -- 多头均价
    avg_short_price REAL,      -- 空头均价
    created_at INTEGER
);

-- 成交记录
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    instrument_code TEXT,
    timestamp INTEGER,
    trade_id TEXT,             -- 成交编号
    direction TEXT,            -- 买卖方向
    open_close TEXT,           -- 开平标志
    price REAL,                -- 成交价格
    volume INTEGER,            -- 成交数量
    order_id TEXT,             -- 委托编号
    trade_time INTEGER,        -- 成交时间
    created_at INTEGER
);

-- 委托订单
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    instrument_code TEXT,
    timestamp INTEGER,
    order_id TEXT,             -- 委托编号
    direction TEXT,            -- 买卖方向
    open_close TEXT,           -- 开平标志
    price REAL,                -- 委托价格
    volume INTEGER,            -- 委托数量
    traded_volume INTEGER,     -- 已成交数量
    status TEXT,               -- 委托状态
    order_time INTEGER,        -- 委托时间
    created_at INTEGER
);

-- 资金账户
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER,
    account_id TEXT,           -- 账户ID
    balance REAL,              -- 账户权益
    available REAL,            -- 可用资金
    margin REAL,                -- 保证金
    commission REAL,            -- 手续费
    float_pnl REAL,            -- 浮动盈亏
    created_at INTEGER
);

-- 合约信息
CREATE TABLE instruments (
    id INTEGER PRIMARY KEY,
    instrument_code TEXT,
    exchange_id TEXT,          -- 交易所ID
    product_id TEXT,           -- 产品ID
    instrument_name TEXT,      -- 合约名称
    delivery_day INTEGER,      -- 交割月份
    list_date TEXT,            -- 上市日期
    expire_date TEXT,          -- 到期日
    contract_multiplier REAL,  -- 合约乘数
    price_tick REAL,           -- 最小变动价位
    created_at INTEGER
);
```

## 运行要求

### 环境变量
```bash
export PYTHONPATH="/mnt/x/LOTT/conda/Lib/site-packages:$PYTHONPATH"
```

### 日志要求
- 日志路径: `X:\LOTT\logs\simnow_YYYYMMDD.log`
- 日志级别: INFO
- 记录内容: 连接状态、订阅结果、数据写入数量、异常信息

### 异常处理
- [ ] 网络断开自动重连
- [ ] 登录超时重新登录
- [ ] 数据写入失败记录错误并继续
- [ ] 进程异常退出保存状态

## 验证清单（明天执行）

### 启动前检查
- [ ] simnow_collector.py 存在
- [ ] 数据库目录可写
- [ ] 日志目录存在
- [ ] conda 环境可用

### 运行时检查
- [ ] 登录成功
- [ ] 合约列表非空
- [ ] 数据写入成功
- [ ] 无异常报错

### 数据验证
- [ ] quotes 表有数据
- [ ] positions 表有数据
- [ ] accounts 表有数据
- [ ] instruments 表有数据

---

## 执行命令（明天使用）

```bash
# 手动测试
cd /mnt/x/LOTT
PYTHONPATH="/mnt/x/LOTT/conda/Lib/site-packages:$PYTHONPATH" /mnt/x/LOTT/conda/python.exe simnow_collector.py
```

```bash
# 检查数据库
sqlite3 /mnt/x/LOTT/src/Data/DataSource/_db/realtime/simnow.db "SELECT COUNT(*) FROM quotes;"
```

```bash
# 查看日志
tail -f /mnt/x/LOTT/logs/simnow_*.log
```
