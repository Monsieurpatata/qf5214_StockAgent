import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime

class SectorInput(BaseModel):
    sector: str = Field(description="股票板块名称（如 '银行'、'新能源'）")
    start_date: str = Field(description="开始日期，格式YYYYMMDD（如 20230101）")
    end_date: str = Field(description="结束日期，格式YYYYMMDD（如 20231231）")

@tool(args_schema=SectorInput)
def get_stock_sector_data(sector: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取指定股票板块的相关数据，并按表格格式返回。

    参数：
    sector (str): 股票板块名称（如 "银行"、"新能源"）
    start_date (str): 开始日期，格式YYYYMMDD
    end_date (str): 结束日期，格式YYYYMMDD

    返回：
    pd.DataFrame: 股票板块的相关数据表
    """
    # 在获取板块数据后添加日期验证
    try:
        datetime.strptime(start_date, "%Y%m%d")
        datetime.strptime(end_date, "%Y%m%d")
    except ValueError:
        raise ValueError("日期格式错误，请使用YYYYMMDD格式")

    # 获取所有行业板块数据（使用 stock_board_industry_name_em）
    try:
        sector_list = ak.stock_board_industry_name_em()
    except Exception as e:
        raise ValueError(f"无法获取行业板块列表。错误：{str(e)}")

    # 检查板块是否存在
    if sector not in sector_list["板块名称"].values:
        raise ValueError(f"无法找到名为 {sector} 的板块，请检查板块名称是否正确。")
    
    # 获取指定板块的成分股数据（使用 stock_board_industry_cons_em）
    try:
        sector_data = ak.stock_board_industry_cons_em(symbol=sector)
    except Exception as e:
        raise ValueError(f"无法获取 {sector} 板块的成分股数据。错误：{str(e)}")

    if sector_data.empty:
        raise ValueError(f"无法获取 {sector} 板块的成分股数据，请检查板块名称是否正确。")

    # 假设数据中包含 '代码' 列（根据实际打印出来的列名调整）
    stock_data_list = []
    for symbol in sector_data["代码"]:  # 使用实际列名来替代 '品种代码'
        data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq", start_date=start_date, end_date=end_date)
        if not data.empty:
            last_data = data.iloc[-1]
            prev_close = data.iloc[-2]["收盘"] if len(data) > 1 else last_data["收盘"]  # 如果没有前一交易日的数据，则使用最新数据
            
            # 计算涨跌幅和涨跌额
            change = last_data["收盘"] - prev_close
            change_percent = (change / prev_close) * 100

            stock_data = {
                "股票代码": symbol,
                "股票名称": sector_data[sector_data["代码"] == symbol]["名称"].values[0],  # 根据实际列名调整
                "日期时间": last_data["日期"],
                "开盘": last_data["开盘"],
                "收盘": last_data["收盘"],
                "最高": last_data["最高"],
                "最低": last_data["最低"],
                "涨跌幅": round(change_percent, 2),  # 单位 %
                "涨跌额": round(change, 2),
                "成交量": int(last_data["成交量"]),  # 成交量
                "成交额": round(last_data["成交额"], 2),  # 成交金额
                "振幅": round(last_data["振幅"], 2),  # 单位 %
                "换手率": round(last_data["换手率"], 2)  # 换手率（%）
            }

            stock_data_list.append(stock_data)

    # 合并所有股票数据
    result_df = pd.DataFrame(stock_data_list)

    return result_df

if __name__ == "__main__":
    # 示例调用
    sector_name = "银行"
    result = get_stock_sector_data.invoke({
        "sector": sector_name,
        "start_date": "20250101",
        "end_date": "20250204"
    })
    print(result)
