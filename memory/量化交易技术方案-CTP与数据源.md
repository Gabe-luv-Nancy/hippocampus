# 量化交易数据与回测系统 - 技术方案

## 目标

使用开源/免费技术框架，实现：

1. **期货、ETF历史数据**（月度到分钟级）的获取与存储
2. **实时数据**（分钟级、Tick级）的接入
3. **量化策略回测与研发**

---

## 一、数据源方案

### 1.1 实时数据（期货）

| 方案           | 描述                  | 费用        | 难度  |
| ------------ | ------------------- | --------- | --- |
| **CTP API**  | 上期技术官方期货接口，支持行情+交易  | 免费（需期货账户） | 中等  |
| **VNPY**     | 开源量化框架，内置CTP接口      | 免费        | 低   |
| **AlgoPlus** | CTP API 的 Python 封装 | 免费        | 低   |
| **TqSdk**    | 天勤量化库，支持期货实时行情      | 免费        | 低   |

**推荐**：从 **TqSdk** 或 **VNPY** 入手最简单的。

### 1.2 历史数据

| 数据源                                    | 覆盖范围     | 费用   | 数据格式             |
| -------------------------------------- | -------- | ---- | ---------------- |
| **Baostock**                           | A股+部分期货  | 免费   | Pandas DataFrame |
| **Tushare**                            | A股、期货、基金 | 免费额度 | Pandas           |
| **AkShare**                            | 财经全品类    | 免费开源 | Pandas           |
| **东方财富爬虫** | 期货、ETF   | 免费   | 需解析              |

**期货历史数据**：

- Tushare Pro（需要积分）
- 东方财富网页端（需要爬虫/浏览器抓取）
- CTP 行情记录（自己接收并存储）

### 1.3 ETF 数据

| 方案                 | 说明          |
| ------------------ | ----------- |
| **Tushare ETF 接口** | 基金数据，支持历史K线 |
| **AkShare ETF**    | 开放式基金数据     |
| **天天基金网爬虫**        | 东方财富旗下，数据全  |

---

## 二、技术框架推荐

### 2.1 整体架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  数据采集层  │ --> │  数据存储层  │ --> │  回测/分析层 │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      v                   v                   v
  TqSdk/VNPY         PostgreSQL           Backtrader
  Baostock           MySQL                VNPY
  AkShare            InfluxDB (时序)      Zipline
```

### 2.2 技术栈

| 层级       | 推荐技术                         |
| -------- | ---------------------------- |
| **编程语言** | Python 3.8+                  |
| **数据获取** | TqSdk、AkShare、Baostock       |
| **数据库**  | PostgreSQL（主）、InfluxDB（时序数据） |
| **回测框架** | Backtrader、VNPY              |
| **数据处理** | Pandas、NumPy                 |
| **可选图表** | PyQtGraph、Matplotlib         |

---

## 三、实施方案

### 阶段一：环境搭建

1. 安装 Python 3.10+
2. 安装必要库：
   
   ```bash
   pip install tqsdk pandas numpy sqlalchemy
   pip install backtrader akshare baostock
   ```

### 阶段二：历史数据获取

**期货分钟数据**：

- TqSdk 示例：
  
  ```python
  from tqsdk import TqApi
  
  api = TqApi()
  klines = api.get_kline_serial("SHFE.rb2505", 60)  # 1分钟K线
  print(klines)
  ```

**A股/ETF日线**：

- Baostock 示例：
  
  ```python
  import baostock as bs
  
  lg = bs.login()
  rs = bs.query_history_k_data_plus("sh.600000",
      "date,open,high,low,close,volume",
      start_date='2020-01-01', end_date='2024-12-31')
  ```

### 阶段三：实时数据接入

使用 TqSdk 接收期货实时行情：

```python
from tqsdk import TqApi, TqAuth

api = TqApi(auth=TqAuth("账号", "密码"))
kline = api.get_kline_serial("SHFE.rb2505", 60)
# 自动推送更新
```

### 阶段四：数据存储

使用 SQLAlchemy 存储到 PostgreSQL：

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost:5432/quant_db')
df.to_sql('futures_minute', engine, if_exists='append')
```

### 阶段五：回测

使用 Backtrader：

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    def next(self):
        if self.data.close[0] > self.data.close[-1]:
            self.buy()

cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
cerebro.run()
```

---

## 四、浏览器调试方案（备选）

如果需要从网页抓取数据（ETF/期货历史K线）：

1. 打开 Chrome 开发者工具（F12）
2. Network 面板 → 筛选 XHR/Fetch
3. 访问目标页面（如东方财富期货行情页）
4. 找到数据请求 API，复制 curl
5. 用 Python requests 模拟请求

**示例**：从天天基金网获取ETF净值数据

---

## 五、下一步行动

1. **确认数据需求**：期货品种？ETF具体代码？
2. **选择数据源**：先用 Baostock 测试 A股数据？
3. **安装环境**：我帮你搭建 Python 环境
4. **先跑通 Demo**：获取一小段数据验证流程

---

需要我帮你开始搭建环境或写测试代码吗？
