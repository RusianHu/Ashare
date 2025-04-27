"""
Ashare MCP Server - 股票行情数据双核心版 MCP 服务
基于 https://github.com/mpquant/Ashare
"""

import json
import requests
import datetime
import asyncio
from typing import Optional, Literal, List, Dict, Any, Union
import pandas as pd
from fastmcp import FastMCP
from pydantic import Field, BaseModel
from typing import Annotated

# 创建 MCP 服务器
mcp = FastMCP(
    name="Ashare MCP",
    instructions="这是一个股票行情数据服务，提供A股市场的行情数据查询功能。",
    dependencies=["pandas", "requests"]
)

# 定义数据模型
class StockData(BaseModel):
    """股票行情数据模型"""
    code: str = Field(description="股票代码")
    data: Dict[str, Any] = Field(description="股票行情数据，DataFrame转换为字典")
    message: str = Field(description="处理消息")

# 腾讯日线
async def get_price_day_tx_async(code: str, end_date: str = '', count: int = 10, frequency: str = '1d') -> pd.DataFrame:
    """日线获取 - 异步版本"""
    unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'  # 判断日线，周线，月线
    if end_date:
        end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
    end_date = '' if end_date == datetime.datetime.now().strftime('%Y-%m-%d') else end_date  # 如果日期今天就变成空
    
    URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'
    
    # 使用异步执行网络请求
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: requests.get(URL))
    st = json.loads(response.content)
    
    ms = 'qfq' + unit
    stk = st['data'][code]
    buf = stk[ms] if ms in stk else stk[unit]  # 指数返回不是qfqday,是day
    
    df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume'], dtype='float')
    df.time = pd.to_datetime(df.time)
    df.set_index(['time'], inplace=True)
    df.index.name = ''  # 处理索引
    
    return df

# 腾讯分钟线
async def get_price_min_tx_async(code: str, end_date: Optional[str] = None, count: int = 10, frequency: str = '1d') -> pd.DataFrame:
    """分钟线获取 - 异步版本"""
    ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1  # 解析K线周期数
    if end_date:
        end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
    
    URL = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
    
    # 使用异步执行网络请求
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: requests.get(URL))
    st = json.loads(response.content)
    
    buf = st['data'][code]['m' + str(ts)]
    df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'n1', 'n2'])
    df = df[['time', 'open', 'close', 'high', 'low', 'volume']]
    df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].astype('float')
    df.time = pd.to_datetime(df.time)
    df.set_index(['time'], inplace=True)
    df.index.name = ''  # 处理索引
    df['close'][-1] = float(st['data'][code]['qt'][code][3])  # 最新基金数据是3位的
    
    return df

# 新浪全周期获取函数
async def get_price_sina_async(code: str, end_date: str = '', count: int = 10, frequency: str = '60m') -> pd.DataFrame:
    """新浪全周期获取函数 - 异步版本"""
    frequency = frequency.replace('1d', '240m').replace('1w', '1200m').replace('1M', '7200m')
    mcount = count
    ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1  # 解析K线周期数
    
    if (end_date != '') & (frequency in ['240m', '1200m', '7200m']):
        end_date = pd.to_datetime(end_date) if not isinstance(end_date, datetime.date) else end_date  # 转换成datetime
        unit = 4 if frequency == '1200m' else 29 if frequency == '7200m' else 1  # 4,29多几个数据不影响速度
        count = count + (datetime.datetime.now() - end_date).days // unit  # 结束时间到今天有多少天自然日(肯定 >交易日)
    
    URL = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}'
    
    # 使用异步执行网络请求
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: requests.get(URL))
    dstr = json.loads(response.content)
    
    df = pd.DataFrame(dstr, columns=['day', 'open', 'high', 'low', 'close', 'volume'])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df.day = pd.to_datetime(df.day)
    df.set_index(['day'], inplace=True)
    df.index.name = ''  # 处理索引
    
    if (end_date != '') & (frequency in ['240m', '1200m', '7200m']):
        return df[df.index <= end_date][-mcount:]  # 日线带结束时间先返回
    
    return df

# MCP 工具 - 获取股票行情数据
@mcp.tool()
async def get_price(
    code: Annotated[str, Field(description="证券代码，如'sh000001'或'000001.XSHG'")],
    end_date: Annotated[str, Field(description="结束日期，格式为'YYYY-MM-DD'")] = '',
    count: Annotated[int, Field(description="获取的K线数量")] = 10,
    frequency: Annotated[Literal['1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M'], 
                         Field(description="K线周期，分钟线：'1m', '5m', '15m', '30m', '60m'，日线：'1d'，周线：'1w'，月线：'1M'")] = '1d',
    fields: Annotated[List[str], Field(description="返回字段列表，默认为全部")] = []
) -> StockData:
    """
    获取股票行情数据，支持分钟线、日线、周线、月线。
    
    Args:
        code: 证券代码，如'sh000001'或'000001.XSHG'
        end_date: 结束日期，格式为'YYYY-MM-DD'
        count: 获取的K线数量
        frequency: K线周期，分钟线：'1m', '5m', '15m', '30m', '60m'，日线：'1d'，周线：'1w'，月线：'1M'
        fields: 返回字段列表，默认为全部
        
    Returns:
        StockData: 包含股票代码、行情数据和处理消息的对象
    """
    try:
        # 证券代码编码兼容处理
        xcode = code.replace('.XSHG', '').replace('.XSHE', '')
        xcode = 'sh' + xcode if ('XSHG' in code) else 'sz' + xcode if ('XSHE' in code) else code

        df = None
        if frequency in ['1d', '1w', '1M']:  # 1d日线 1w周线 1M月线
            try:
                df = await get_price_sina_async(xcode, end_date=end_date, count=count, frequency=frequency)  # 主力
            except Exception as e:
                df = await get_price_day_tx_async(xcode, end_date=end_date, count=count, frequency=frequency)  # 备用

        if frequency in ['1m', '5m', '15m', '30m', '60m']:  # 分钟线 ,1m只有腾讯接口 5分钟5m 60分钟60m
            if frequency in '1m':
                df = await get_price_min_tx_async(xcode, end_date=end_date, count=count, frequency=frequency)
            else:
                try:
                    df = await get_price_sina_async(xcode, end_date=end_date, count=count, frequency=frequency)  # 主力
                except Exception as e:
                    df = await get_price_min_tx_async(xcode, end_date=end_date, count=count, frequency=frequency)  # 备用

        # 将DataFrame转换为字典
        data_dict = df.reset_index().to_dict(orient='records')
        
        return StockData(
            code=code,
            data={"records": data_dict, "columns": list(df.reset_index().columns)},
            message=f"成功获取{code}的{frequency}周期数据，共{len(df)}条记录"
        )
    except Exception as e:
        return StockData(
            code=code,
            data={},
            message=f"获取数据失败: {str(e)}"
        )
