# Ashare-MCP

Ashare-MCP 是一个基于 [mpquant/Ashare](https://github.com/mpquant/Ashare) 的股票行情数据服务，通过 MCP (Model Context Protocol) 提供 A 股市场的行情数据查询功能。

## 特性

- 支持多种周期的行情数据：分钟线（1m, 5m, 15m, 30m, 60m）、日线（1d）、周线（1w）、月线（1M）
- 支持多种股票代码格式：通达信格式（sh000001）、聚宽格式（000001.XSHG）
- 双核心数据源：新浪财经和腾讯财经，提高数据获取的稳定性
- 异步处理，提高性能
- 简单易用的 API 接口

## 安装

```bash
pip install ashare_mcp
```

## 使用方法

### 作为 MCP 服务使用

1. 在 MCP 配置文件中添加服务配置：

```json
{
  "mcpServers": {
    "ashare-mcp": {
      "command": "python",
      "args": [
        "-m",
        "ashare_mcp"
      ],
      "alwaysAllow": [
        "get_price"
      ],
      "disabled": false
    }
  }
}
```

2. 在 MCP 客户端中调用：

```python
# 获取上证指数日线数据
result = await get_price_ashare_mcp(code="sh000001", count=5, frequency="1d")
print(result)

# 获取贵州茅台15分钟线数据
result = await get_price_ashare_mcp(code="sh600519", count=5, frequency="15m")
print(result)
```

### 作为独立服务运行

```bash
# 使用标准输入输出模式
ashare-mcp

# 使用 HTTP 模式
fastmcp serve ashare_mcp
```

## API 参考

### get_price

获取股票行情数据，支持分钟线、日线、周线、月线。

**参数：**

- `code`：证券代码，如'sh000001'或'000001.XSHG'
- `end_date`：结束日期，格式为'YYYY-MM-DD'，默认为空（当前日期）
- `count`：获取的K线数量，默认为10
- `frequency`：K线周期，可选值：'1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'，默认为'1d'
- `fields`：返回字段列表，默认为全部

**返回：**

包含股票代码、行情数据和处理消息的对象。

## 示例

```python
# 获取上证指数最近5天的日线数据
result = await get_price_ashare_mcp(code="sh000001", count=5, frequency="1d")

# 获取贵州茅台指定日期的历史数据
result = await get_price_ashare_mcp(code="sh600519", end_date="2023-01-01", count=10, frequency="1d")

# 获取分钟线数据
result = await get_price_ashare_mcp(code="sh600519", count=5, frequency="15m")
```

## 依赖

- fastmcp>=0.1.0
- pandas
- requests

## 许可证

[MIT](LICENSE)