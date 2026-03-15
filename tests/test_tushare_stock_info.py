#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 _get_tushare_stock_info 函数

使用方法:
    cd /Users/shaozhewang/work/opensource/TradingAgents-CN
    python tests/test_tushare_stock_info.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('DASHSCOPE_API_KEY', 'sk-test')

from tradingagents.dataflows.data_source_manager import DataSourceManager

def test_tushare_stock_info():
    """测试 Tushare 获取股票信息"""
    print("=" * 70)
    print("  测试 _get_tushare_stock_info 函数")
    print("=" * 70)

    # 测试股票：赛分科技 (688758) - 科创板
    test_symbols = [
        ("688758", "赛分科技 - 科创板"),
        ("000001", "平安银行 - 深市主板"),
        ("600000", "浦发银行 - 沪市主板"),
        ("300750", "宁德时代 - 创业板"),
    ]

    manager = DataSourceManager()

    # 检查 Tushare 是否可用
    from tradingagents.dataflows.data_source_manager import ChinaDataSource
    if ChinaDataSource.TUSHARE not in manager.available_sources:
        print("⚠️ Tushare 数据源不可用，跳过测试")
        return False

    print(f"\n✅ Tushare 数据源可用")
    print(f"   可用数据源：{[s.value for s in manager.available_sources]}")

    results = []

    for symbol, description in test_symbols:
        print(f"\n{'-' * 70}")
        print(f"  测试：{symbol} ({description})")
        print(f"{'-' * 70}")

        try:
            # 调用 _get_tushare_stock_info 方法
            result = manager._get_tushare_stock_info(symbol)

            print(f"  返回结果:")
            for key, value in result.items():
                if value and key != 'error':
                    print(f"    {key}: {value}")

            # 验证必需字段
            required_fields = ['symbol', 'name', 'source']
            missing_fields = [f for f in required_fields if f not in result]

            if missing_fields:
                print(f"  ❌ 缺少必需字段：{missing_fields}")
                results.append(False)
            elif result.get('name') == f'股票{symbol}':
                print(f"  ⚠️ 未获取到有效股票名称")
                results.append(False)
            else:
                print(f"  ✅ 验证通过")
                results.append(True)

        except Exception as e:
            print(f"  ❌ 异常：{e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # 总结
    print(f"\n{'=' * 70}")
    print(f"  测试总结：{sum(results)}/{len(results)} 通过")
    print(f"{'=' * 70}")

    return all(results)


def test_data_format_compatibility():
    """测试数据格式与下游兼容性"""
    print(f"\n{'=' * 70}")
    print(f"  测试数据格式与下游兼容性")
    print(f"{'=' * 70}")

    manager = DataSourceManager()

    # 模拟下游使用场景
    symbol = "688758"

    try:
        result = manager._get_tushare_stock_info(symbol)

        # 验证字段类型
        print(f"\n  字段类型验证:")
        field_checks = {
            'symbol': str,
            'name': str,
            'area': str,
            'industry': str,
            'market': str,
            'list_date': str,
            'source': str,
        }

        all_passed = True
        for field, expected_type in field_checks.items():
            if field in result:
                actual_type = type(result[field]).__name__
                is_correct = isinstance(result[field], expected_type)
                status = "✅" if is_correct else "❌"
                print(f"    {status} {field}: {actual_type}")
                if not is_correct:
                    all_passed = False
            else:
                print(f"    ⚠️ {field}: 不存在")

        # 验证下游关键字段
        print(f"\n  下游使用场景验证:")

        # 场景 1: fundamentals_snapshot.py 需要 ts_code
        ts_code = result.get('ts_code')
        if ts_code:
            print(f"    ✅ ts_code: {ts_code}")
        else:
            print(f"    ⚠️ ts_code: 不存在（fundamentals_snapshot 可能失败）")

        # 场景 2: 需要 name 字段
        if result.get('name'):
            print(f"    ✅ name: {result['name']}")
        else:
            print(f"    ❌ name: 不存在")
            all_passed = False

        return all_passed

    except Exception as e:
        print(f"  ❌ 验证失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  _get_tushare_stock_info 函数验证")
    print("=" * 70 + "\n")

    # 测试基本功能
    test1_passed = test_tushare_stock_info()

    # 测试格式兼容性
    test2_passed = test_data_format_compatibility()

    # 最终结果
    print(f"\n{'=' * 70}")
    print(f"  最终结果")
    print(f"{'=' * 70}")
    print(f"  基本功能测试：{'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"  格式兼容性测试：{'✅ 通过' if test2_passed else '❌ 失败'}")
    print(f"{'=' * 70}\n")

    sys.exit(0 if (test1_passed and test2_passed) else 1)
