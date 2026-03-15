#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛分科技 (688758) 股票分析 - 简化测试用例

快速测试 TradingAgents 框架对 A 股科创板股票的分析能力。
不包含交互式的完整测试请使用：test_saifen_tech_688758.py

使用方法:
    python tests/test_saifen_tech_688758_simple.py

测试目标：
- 验证数据源可用性 (AKShare)
- 验证基础数据获取 (市场数据、基本面数据)
- 验证 LLM 连接配置

赛分科技基本信息:
- 股票代码：688758（科创板）
- 公司名称：江苏赛分科技股份有限公司
- 主营业务：色谱分离材料和技术研发
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / ".env", override=True)


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """主测试函数"""
    print_section("赛分科技 (688758) 股票分析 - 简化测试")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标股票：688758 - 赛分科技 (A 股科创板)")

    results = {}

    # ==================== 测试 1: 数据源可用性 ====================
    print_section("测试 1: 数据源可用性检查")

    try:
        from tradingagents.dataflows.providers.china.akshare import AKShareProvider
        provider = AKShareProvider()
        print(f"✅ AKShare 数据源初始化成功")

        # 使用 akshare 直接查询
        import akshare as ak
        stock_list = ak.stock_info_a_code_name()
        saifen = stock_list[stock_list['name'].str.contains('赛分', na=False)]
        if not saifen.empty:
            print(f"✅ 找到赛分科技 (688758)")
            print(f"   公司名称：{saifen.iloc[0]['name']}")
            print(f"   股票代码：{saifen.iloc[0]['code']}")
        else:
            print(f"⚠️ 未在股票列表中找到赛分科技")

        results["数据源测试"] = True

    except Exception as e:
        print(f"❌ 数据源测试失败：{e}")
        results["数据源测试"] = False

    # ==================== 测试 2: 市场数据获取 ====================
    print_section("测试 2: 市场数据获取")

    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config['online_tools'] = True
        toolkit = Toolkit(config=config)

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

        market_data = toolkit.get_stock_market_data_unified.invoke({
            'ticker': "688758",
            'start_date': start_date,
            'end_date': end_date
        })

        if market_data:
            print(f"✅ 市场数据获取成功，数据长度：{len(market_data)} 字符")
            results["市场数据获取"] = True
        else:
            print(f"⚠️ 市场数据返回为空")
            results["市场数据获取"] = False

    except Exception as e:
        print(f"❌ 市场数据获取失败：{e}")
        results["市场数据获取"] = False

    # ==================== 测试 3: 基本面数据获取 ====================
    print_section("测试 3: 基本面数据获取")

    try:
        fundamentals_data = toolkit.get_stock_fundamentals_unified.invoke({
            'ticker': "688758",
            'start_date': start_date,
            'end_date': end_date,
            'curr_date': end_date
        })

        if fundamentals_data:
            print(f"✅ 基本面数据获取成功，数据长度：{len(fundamentals_data)} 字符")

            # 检查关键指标
            has_pe = "PE" in fundamentals_data or "市盈率" in fundamentals_data
            has_pb = "PB" in fundamentals_data or "市净率" in fundamentals_data

            if has_pe:
                print(f"   ✓ 包含市盈率 (PE) 指标")
            if has_pb:
                print(f"   ✓ 包含市净率 (PB) 指标")

            results["基本面数据获取"] = True
        else:
            print(f"⚠️ 基本面数据返回为空")
            results["基本面数据获取"] = False

    except Exception as e:
        print(f"❌ 基本面数据获取失败：{e}")
        results["基本面数据获取"] = False

    # ==================== 测试 4: LLM 配置检查 ====================
    print_section("测试 4: LLM 供应商配置检查")

    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    print(f"DASHSCOPE_API_KEY: {'✅ 已设置' if dashscope_key else '❌ 未设置'}")
    print(f"FINNHUB_API_KEY: {'✅ 已设置' if finnhub_key else '❌ 未设置'}")

    if not dashscope_key:
        print("\n⚠️ 警告：未设置 DASHSCOPE_API_KEY")
        print("   请在.env 文件中配置：DASHSCOPE_API_KEY=your_api_key")
        results["LLM 配置测试"] = False
    else:
        # 测试 LLM 连接
        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="qwen-plus",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=dashscope_key,
                temperature=0.3,
                max_tokens=100,
                timeout=30
            )

            response = llm.invoke("你好")
            print(f"✅ LLM 连接测试成功")
            print(f"   模型响应：{response.content[:50]}...")
            results["LLM 配置测试"] = True

        except Exception as e:
            print(f"❌ LLM 连接测试失败：{e}")
            results["LLM 配置测试"] = False

    # ==================== 测试总结 ====================
    print_section("测试总结")

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\n总计：{passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
    elif passed > 0:
        print("\n⚠️ 部分测试通过，请检查失败项")
    else:
        print("\n❌ 所有测试失败，请检查环境配置")

    print("\n" + "=" * 70)
    print("提示：如需运行完整的分析流程测试，请使用:")
    print("  python tests/test_saifen_tech_688758.py")
    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
