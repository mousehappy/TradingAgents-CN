#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛分科技 (688758) 股票分析测试用例

测试目标：验证 TradingAgents 框架对 A 股科创板股票的分析能力
赛分科技基本信息：
- 股票代码：688758（科创板）
- 公司名称：江苏赛分科技股份有限公司
- 主营业务：色谱分离材料和技术研发

使用方法:
    python tests/test_saifen_tech_688758.py

依赖:
    - 已配置 DASHSCOPE_API_KEY 或其他 LLM API Key
    - 已安装 AKShare 数据源
    - 已同步股票基础数据
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


# ==================== 测试配置 ====================

TEST_CONFIG = {
    "ticker": "002273",              # 赛分科技股票代码
    "company_name": "水晶光电",        # 公司名称
    "market": "A 股",            # 市场类型
    "analysis_date": None,           # 分析日期（None 表示使用最近日期）
    "selected_analysts": [           # 选择的分析师
        "market",        # 市场分析师（技术分析）
        "fundamentals",  # 基本面分析师
        "news",          # 新闻分析师
        "social",        # 社交媒体分析师
    ],
    "research_depth": 3,             # 研究深度 (1=快速，2=标准，3=深度)
    "online_tools": True,            # 使用在线数据
    "memory_enabled": False,         # 启用历史记忆（测试时可禁用加快速度）
}


# ==================== 测试函数 ====================

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_data_source():
    """测试 1: 数据源可用性"""
    print_section("测试 1: 数据源可用性检查")

    try:
        from tradingagents.dataflows.providers.china.akshare import AKShareProvider

        provider = AKShareProvider()
        print(f"✅ AKShare 数据源初始化成功")

        # 测试获取股票基本信息（使用同步方法）
        try:
            import akshare as ak
            stock_list = ak.stock_info_a_code_name()
            saifen = stock_list[stock_list['name'].str.contains('赛分', na=False)]
            if not saifen.empty:
                print(f"✅ 找到赛分科技 (688758) 在股票列表中")
                print(f"   公司名称：{saifen.iloc[0]['name']}")
                print(f"   股票代码：{saifen.iloc[0]['code']}")
            else:
                print(f"⚠️ 未在股票列表中找到赛分科技")
        except Exception as e:
            print(f"⚠️ 获取股票列表失败：{e}")

        return True

    except Exception as e:
        print(f"❌ 数据源测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_data_fetch():
    """测试 2: 基础数据获取"""
    print_section("测试 2: 基础数据获取测试")

    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config['online_tools'] = True
        config['research_depth'] = '标准'

        toolkit = Toolkit(config=config)

        # 测试市场数据
        print("\n📊 测试市场数据获取...")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

        # 使用 invoke 方法调用工具
        market_data = toolkit.get_stock_market_data_unified.invoke({
            'ticker': "688758",
            'start_date': start_date,
            'end_date': end_date
        })
        if market_data:
            print(f"✅ 市场数据获取成功，数据长度：{len(market_data)} 字符")
        else:
            print(f"⚠️ 市场数据返回为空")

        # 测试基本面数据
        print("\n📈 测试基本面数据获取...")
        fundamentals_data = toolkit.get_stock_fundamentals_unified.invoke({
            'ticker': "688758",
            'start_date': start_date,
            'end_date': end_date,
            'curr_date': end_date
        })
        if fundamentals_data:
            print(f"✅ 基本面数据获取成功，数据长度：{len(fundamentals_data)} 字符")
            # 检查是否包含关键指标
            if "PE" in fundamentals_data or "市盈率" in fundamentals_data:
                print(f"   ✓ 包含市盈率 (PE) 指标")
            if "PB" in fundamentals_data or "市净率" in fundamentals_data:
                print(f"   ✓ 包含市净率 (PB) 指标")
        else:
            print(f"⚠️ 基本面数据返回为空")

        return True

    except Exception as e:
        print(f"❌ 数据获取测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_provider():
    """测试 3: LLM 供应商配置"""
    print_section("测试 3: LLM 供应商配置检查")

    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    print(f"DASHSCOPE_API_KEY: {'✅ 已设置' if dashscope_key else '❌ 未设置'}")
    print(f"FINNHUB_API_KEY: {'✅ 已设置' if finnhub_key else '❌ 未设置'}")

    if not dashscope_key:
        print("\n⚠️ 警告：未设置 DASHSCOPE_API_KEY，LLM 分析功能将无法使用")
        print("   请在.env 文件中配置：DASHSCOPE_API_KEY=your_api_key")
        return False

    # 测试 LLM 连接
    try:
        from langchain_openai import ChatOpenAI

        # 尝试创建 LLM 实例（测试配置）
        llm = ChatOpenAI(
            model="qwen-plus",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=dashscope_key,
            temperature=0.3,
            max_tokens=100,
            timeout=30
        )

        # 简单测试调用
        response = llm.invoke("你好，请用一句话介绍你自己")
        print(f"✅ LLM 连接测试成功")
        print(f"   模型响应：{response.content[:50]}...")
        return True

    except Exception as e:
        print(f"❌ LLM 连接测试失败：{e}")
        return False


def test_full_analysis():
    """测试 4: 完整分析流程"""
    print_section("测试 4: 完整分析流程测试")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # 创建分析配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "dashscope"
        config["deep_think_llm"] = "qwen-plus"
        config["quick_think_llm"] = "qwen-plus"
        config["backend_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        config["memory_enabled"] = TEST_CONFIG["memory_enabled"]
        config["online_tools"] = TEST_CONFIG["online_tools"]
        config["research_depth"] = TEST_CONFIG["research_depth"]

        # 设置分析日期
        analysis_date = TEST_CONFIG["analysis_date"]
        if not analysis_date:
            analysis_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n📋 分析配置:")
        print(f"   股票代码：{TEST_CONFIG['ticker']} ({TEST_CONFIG['company_name']})")
        print(f"   市场类型：{TEST_CONFIG['market']}")
        print(f"   分析日期：{analysis_date}")
        print(f"   分析师：{', '.join(TEST_CONFIG['selected_analysts'])}")
        print(f"   研究深度：{TEST_CONFIG['research_depth']} (1=快速，2=标准，3=深度)")
        print(f"   在线工具：{'启用' if TEST_CONFIG['online_tools'] else '禁用'}")
        print(f"   历史记忆：{'启用' if TEST_CONFIG['memory_enabled'] else '禁用'}")

        # 创建分析图
        print(f"\n🚀 创建 TradingAgents 分析图...")
        graph = TradingAgentsGraph(
            selected_analysts=TEST_CONFIG["selected_analysts"],
            config=config,
            debug=True
        )
        print(f"✅ 分析图创建成功")

        # 执行分析
        print(f"\n🔍 开始执行分析 (这可能需要 3-5 分钟)...")
        import time
        start_time = time.time()

        state, decision = graph.propagate(
            TEST_CONFIG["ticker"],
            analysis_date
        )

        elapsed_time = time.time() - start_time
        print(f"\n✅ 分析完成！耗时：{elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")

        # 输出分析结果
        print_section("分析结果")

        print(f"\n📊 最终投资决策:")
        print(f"   建议操作：{decision.get('action', 'N/A')}")
        print(f"   置信度：{decision.get('confidence', 'N/A')}")
        print(f"   目标价格：{decision.get('target_price', 'N/A')}")
        print(f"   止损价格：{decision.get('stop_loss', 'N/A')}")

        # 输出决策理由
        if decision.get('reasoning'):
            print(f"\n💡 决策理由摘要:")
            reasoning = decision.get('reasoning', '')
            if len(reasoning) > 500:
                print(f"   {reasoning[:500]}...")
                print(f"   ...(完整理由见日志文件)")
            else:
                print(f"   {reasoning}")

        # 输出导出文件路径
        print(f"\n📁 分析结果已导出到文件:")
        print(f"   路径：./results/analysis_reports/{TEST_CONFIG['ticker']}_{analysis_date.replace('-', '')}.md")

        return True, state, decision

    except Exception as e:
        print(f"❌ 完整分析测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_only_market_analyst():
    """测试 5: 仅使用市场分析师的快速测试"""
    print_section("测试 5: 仅市场分析师快速测试")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "dashscope"
        config["deep_think_llm"] = "qwen3.5-plus"
        config["quick_think_llm"] = "qwen-plus"
        config["backend_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        config["online_tools"] = True
        config["memory_enabled"] = False  # 禁用记忆加快速度

        print(f"\n🚀 创建简化分析图 (仅市场分析师)...")
        graph = TradingAgentsGraph(
            selected_analysts=["market"],
            config=config,
            debug=True
        )

        analysis_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"🔍 开始分析 {TEST_CONFIG['ticker']}...")

        import time
        start_time = time.time()

        # 使用 try-except 捕获可能的错误
        result = graph.propagate(TEST_CONFIG["ticker"], analysis_date)

        # 处理返回值
        if isinstance(result, tuple) and len(result) == 2:
            state, decision = result
        elif isinstance(result, dict):
            # 如果返回的是字典，尝试从中提取决策
            state = result
            decision = state.get("final_trade_decision", {})
        else:
            print(f"⚠️ 未知返回类型：{type(result)}")
            return False

        elapsed_time = time.time() - start_time
        print(f"✅ 快速分析完成！耗时：{elapsed_time:.2f} 秒")

        # 输出决策信息
        if decision:
            print(f"   建议：{decision.get('action', 'N/A')}")
            print(f"   置信度：{decision.get('confidence', 'N/A')}")
        else:
            print(f"   决策：未生成")

        return True

    except Exception as e:
        print(f"❌ 快速分析测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print_section("赛分科技 (688758) 股票分析测试套件")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标股票：{TEST_CONFIG['ticker']} - {TEST_CONFIG['company_name']}")
    print(f"市场类型：{TEST_CONFIG['market']}")

    results = {
        "数据源测试": test_data_source(),
        "基础数据获取": test_basic_data_fetch(),
        "LLM 配置测试": test_llm_provider(),
    }

    # 根据 LLM 配置决定是否运行完整分析
    run_full = False
    if results["LLM 配置测试"]:
        # 自动运行快速分析，不交互式选择
        print("\n" + "=" * 70)
        print("  LLM 配置正确，运行快速分析测试...")
        print("=" * 70)
        results["快速分析"] = test_only_market_analyst()
    else:
        print("\n⚠️ 由于 LLM 未配置，跳过分析测试")
        results["完整分析"] = "跳过"
        results["快速分析"] = "跳过"

    # 输出测试总结
    print_section("测试总结")

    for test_name, result in results.items():
        status = "✅ 通过" if result is True else ("❌ 失败" if result is False else "⊘ 跳过")
        print(f"  {test_name}: {status}")

    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not True or r is not False])

    print(f"\n总计：{passed}/{len(results)} 测试通过")

    if passed == len(results):
        print("\n🎉 所有测试通过！")
    elif passed > 0:
        print("\n⚠️ 部分测试通过，请检查失败项")
    else:
        print("\n❌ 所有测试失败，请检查环境配置")


# ==================== 命令行交互模式 ====================

def interactive_mode():
    """交互模式"""
    print_section("赛分科技 (688758) 分析 - 交互模式")

    print("\n请选择测试模式:")
    print("  1. 运行所有测试")
    print("  2. 仅测试数据源")
    print("  3. 仅测试数据获取")
    print("  4. 运行完整分析流程")
    print("  5. 运行快速分析 (仅市场分析师)")

    choice = input("\n请输入选择 (1-5): ").strip()

    if choice == "1":
        run_all_tests()
    elif choice == "2":
        test_data_source()
    elif choice == "3":
        test_basic_data_fetch()
    elif choice == "4":
        test_full_analysis()
    elif choice == "5":
        test_only_market_analyst()
    else:
        print("无效选择")


# ==================== 主程序 ====================

if __name__ == "__main__":
    # 检查是否传入交互模式参数
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        # 默认运行所有测试
        test_full_analysis()
