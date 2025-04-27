<p align="center"><h1>Ashare-MCP</h1></p>
<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" />
  <img src="https://img.shields.io/badge/MCP-fastmcp-green" />
  <img src="https://img.shields.io/badge/data-A%E8%82%A1-red" />
  <img src="https://img.shields.io/badge/status-active-success" />
  <img src="https://img.shields.io/github/stars/RusianHu/Ashare-mcp?style=social" />
</p>

Ashare-MCP 是一个基于 [mpquant/Ashare](https://github.com/mpquant/Ashare) 的股票行情数据服务，通过 MCP (Model Context Protocol) 提供 A 股市场的行情数据查询功能。

## 特性

- 支持多种周期的行情数据：分钟线（1m, 5m, 15m, 30m, 60m）、日线（1d）、周线（1w）、月线（1M）
- 支持多种股票代码格式：通达信格式（sh000001）、聚宽格式（000001.XSHG）
- 双核心数据源：新浪财经和腾讯财经，提高数据获取的稳定性
- 异步处理，提高性能
- 简单易用的 API 接口

## 安装

```bash
# 通过 GitHub 安装
pip install git+https://github.com/RusianHu/Ashare-mcp.git

# 如果需要使用代理
pip install git+https://github.com/RusianHu/Ashare-mcp.git --proxy socks5://127.0.0.1:10808

# 通过本地安装（开发模式）
git clone https://github.com/RusianHu/Ashare-mcp.git
cd Ashare-mcp
pip install -e .
```

## 使用方法

### 作为 MCP 服务使用

在 MCP 配置文件中添加服务配置：

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

### 作为独立服务运行

```bash
# 使用标准输入输出模式
ashare-mcp

# 使用 HTTP 模式
fastmcp serve ashare_mcp
```

## MCP 工具函数

<details open>
<summary><b>get_price</b> - 获取股票行情数据</summary>

获取股票行情数据，支持分钟线、日线、周线、月线。

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `code` | 证券代码，如'sh000001'或'000001.XSHG' | string | - |
| `end_date` | 结束日期，格式为'YYYY-MM-DD' | string | 当前日期 |
| `count` | 获取的K线数量 | integer | 10 |
| `frequency` | K线周期，可选值：'1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M' | string | '1d' |
| `fields` | 返回字段列表 | array | 全部 |

**返回值：** 包含股票代码、行情数据和处理消息的对象。
</details>

## 示例

<details open>
<summary><b>代码示例</b></summary>

```python
# 获取上证指数最近5天的日线数据
result = await get_price_ashare_mcp(code="sh000001", count=5, frequency="1d")

# 获取贵州茅台指定日期的历史数据
result = await get_price_ashare_mcp(code="sh600519", end_date="2023-01-01", count=10, frequency="1d")

# 获取分钟线数据
result = await get_price_ashare_mcp(code="sh600519", count=5, frequency="15m")
```
</details>

## 依赖

- fastmcp>=0.1.0
- pandas
- requests

## 贡献

欢迎提交 Issues 和 Pull Requests 来帮助改进这个项目！

## 许可证

[MIT](LICENSE)

Copyright © 2025 [RusianHu](https://github.com/RusianHu)