#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析结果导出工具
将 AI 分析过程和结果输出到文件，按角色和阶段分段输出
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('agents')


class AnalysisResultExporter:
    """分析结果导出器 - 将完整的 AI 分析过程导出到文件"""

    def __init__(self, output_dir: str = None):
        """
        初始化导出器

        Args:
            output_dir: 输出目录，默认为 ./results/analysis_reports
        """
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "results", "analysis_reports")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 [Exporter] 输出目录：{self.output_dir}")

    def export(self, ticker: str, trade_date: str, state: Dict[str, Any], decision: Dict[str, Any],
               execution_log: List[Dict] = None) -> str:
        """
        导出分析结果到文件

        Args:
            ticker: 股票代码
            trade_date: 交易日期
            state: 完整的分析状态
            decision: 最终投资决策
            execution_log: 执行日志（可选，包含每个节点的详细输出）

        Returns:
            导出文件的路径
        """
        # 生成文件名：股票代码_日期.md
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{trade_date.replace('-', '')}.md"
        filepath = self.output_dir / filename

        logger.info(f"📝 [Exporter] 开始导出分析结果：{filepath}")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 1. 写入文件头
                self._write_header(f, ticker, trade_date, state, decision)

                # 2. 写入股票基本信息
                self._write_stock_info(f, state)

                # 3. 写入各分析师的分析报告
                self._write_analyst_reports(f, state)

                # 4. 写入投资辩论过程
                self._write_investment_debate(f, state)

                # 5. 写入风险分析辩论
                self._write_risk_debate(f, state)

                # 6. 写入最终投资决策
                self._write_final_decision(f, decision)

                # 7. 写入执行日志（如果有）
                if execution_log:
                    self._write_execution_log(f, execution_log)

                # 8. 写入性能指标
                self._write_performance_metrics(f, state)

                # 9. 写入文件尾
                self._write_footer(f)

            logger.info(f"✅ [Exporter] 分析结果导出成功：{filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ [Exporter] 导出失败：{e}")
            raise

    def _write_header(self, f, ticker: str, trade_date: str, state: Dict, decision: Dict):
        """写入文件头"""
        f.write("# " + "=" * 80 + "\n")
        f.write(f"#  股票分析报告 - {ticker}\n")
        f.write("# " + "=" * 80 + "\n\n")

        f.write(f"**分析日期**: {trade_date}\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 模型信息
        model_info = decision.get('model_info', '未知') if decision else '未知'
        f.write(f"**使用模型**: {model_info}\n\n")

        f.write("---\n\n")

    def _write_stock_info(self, f, state: Dict):
        """写入股票基本信息"""
        f.write("## 📊 第一部分：股票基本信息\n\n")

        company_name = state.get('company_of_interest', '未知')
        f.write(f"- **公司名称**: {company_name}\n")

        # 从市场报告中提取股票信息
        market_report = state.get('market_report', '')
        if market_report:
            # 尝试提取股票基本信息
            if '股票代码' in market_report:
                f.write(f"- **市场报告**: 已获取\n")

        f.write("\n---\n\n")

    def _write_analyst_reports(self, f, state: Dict):
        """写入各分析师的报告"""
        f.write("## 📈 第二部分：分析师报告\n\n")

        # 1. 市场分析师报告
        if 'market_report' in state and state['market_report']:
            f.write("### 🧑‍💼 2.1 市场分析师报告\n\n")
            f.write(state['market_report'])
            f.write("\n\n")

        # 2. 基本面分析师报告
        if 'fundamentals_report' in state and state['fundamentals_report']:
            f.write("### 🧑‍💼 2.2 基本面分析师报告\n\n")
            f.write(state['fundamentals_report'])
            f.write("\n\n")

        # 3. 新闻分析师报告
        if 'news_report' in state and state['news_report']:
            f.write("### 🧑‍💼 2.3 新闻分析师报告\n\n")
            f.write(state['news_report'])
            f.write("\n\n")

        # 4. 社交媒体/情绪分析师报告
        if 'sentiment_report' in state and state['sentiment_report']:
            f.write("### 🧑‍💼 2.4 情绪分析师报告\n\n")
            f.write(state['sentiment_report'])
            f.write("\n\n")

        f.write("---\n\n")

    def _write_investment_debate(self, f, state: Dict):
        """写入投资辩论过程"""
        f.write("## 💼 第三部分：投资辩论过程\n\n")

        # 检查是否有辩论历史
        invest_debate_state = state.get('invest_debate_state', {})
        history = invest_debate_state.get('history', [])

        if history:
            f.write(f"**辩论轮数**: {len(history)}\n\n")

            # 解析并输出每一轮辩论
            for i, entry in enumerate(history, 1):
                if isinstance(entry, str):
                    # 尝试解析字符串格式的辩论记录
                    if 'Bull' in entry or 'Bear' in entry or 'Manager' in entry:
                        f.write(f"### 第 {i} 轮\n\n")
                        f.write(entry)
                        f.write("\n\n")
                elif isinstance(entry, dict):
                    # 处理字典格式的辩论记录
                    speaker = entry.get('speaker', '未知')
                    content = entry.get('content', '')
                    f.write(f"### 第 {i} 轮 - {speaker}\n\n")
                    f.write(content)
                    f.write("\n\n")
        else:
            # 从 investment_plan 中提取信息
            if 'investment_plan' in state and state['investment_plan']:
                f.write("### 投资计划\n\n")
                f.write(state['investment_plan'])
                f.write("\n\n")

        f.write("---\n\n")

    def _write_risk_debate(self, f, state: Dict):
        """写入风险分析辩论"""
        f.write("## ⚠️ 第四部分：风险分析辩论\n\n")

        risk_debate_state = state.get('risk_debate_state', {})

        # 1. 激进分析师观点
        if 'current_risky_response' in risk_debate_state and risk_debate_state['current_risky_response']:
            f.write("### 🔴 4.1 激进分析师观点\n\n")
            f.write(risk_debate_state['current_risky_response'])
            f.write("\n\n")

        # 2. 保守分析师观点
        if 'current_safe_response' in risk_debate_state and risk_debate_state['current_safe_response']:
            f.write("### 🟢 4.2 保守分析师观点\n\n")
            f.write(risk_debate_state['current_safe_response'])
            f.write("\n\n")

        # 3. 中性分析师观点
        if 'current_neutral_response' in risk_debate_state and risk_debate_state['current_neutral_response']:
            f.write("### 🟡 4.3 中性分析师观点\n\n")
            f.write(risk_debate_state['current_neutral_response'])
            f.write("\n\n")

        # 4. 风险法官最终裁决
        if 'judge_decision' in risk_debate_state and risk_debate_state['judge_decision']:
            f.write("### ⚖️ 4.4 风险法官裁决\n\n")
            f.write(risk_debate_state['judge_decision'])
            f.write("\n\n")

        f.write("---\n\n")

    def _write_final_decision(self, f, decision: Dict):
        """写入最终投资决策"""
        f.write("## 🎯 第五部分：最终投资决策\n\n")

        if not decision:
            f.write("*未生成有效决策*\n\n")
            return

        # 1. 核心决策
        f.write("### 📋 决策摘要\n\n")
        f.write(f"**建议操作**: {decision.get('action', 'N/A')}\n\n")
        f.write(f"**置信度**: {decision.get('confidence', 'N/A')}\n\n")
        f.write(f"**目标价格**: {decision.get('target_price', 'N/A')}\n\n")
        f.write(f"**止损价格**: {decision.get('stop_loss', 'N/A')}\n\n")

        # 2. 决策理由
        if 'reasoning' in decision and decision['reasoning']:
            f.write("### 💡 决策理由\n\n")
            f.write(decision['reasoning'])
            f.write("\n\n")

        # 3. 模型信息
        if 'model_info' in decision and decision['model_info']:
            f.write(f"### 🤖 AI 模型信息\n\n")
            f.write(f"- **模型**: {decision['model_info']}\n\n")

        f.write("---\n\n")

    def _write_execution_log(self, f, execution_log: List[Dict]):
        """写入执行日志（详细的 AI 分析过程）"""
        f.write("## 📝 第六部分：详细执行日志\n\n")

        if not execution_log:
            f.write("*无详细执行日志*\n\n")
            return

        f.write(f"**执行步骤数**: {len(execution_log)}\n\n")

        for i, entry in enumerate(execution_log, 1):
            node_name = entry.get('node_name', '未知节点')
            content = entry.get('content', '')
            timestamp = entry.get('timestamp', '')

            f.write(f"### 步骤 {i}: {node_name}\n\n")
            if timestamp:
                f.write(f"*时间*: {timestamp}\n\n")
            f.write(content)
            f.write("\n\n")

        f.write("---\n\n")

    def _write_performance_metrics(self, f, state: Dict):
        """写入性能指标"""
        f.write("## ⏱️ 第七部分：分析性能指标\n\n")

        performance = state.get('performance_metrics', {})

        if performance:
            f.write(f"- **总耗时**: {performance.get('total_elapsed', 'N/A')} 秒\n")
            f.write(f"- **节点数量**: {performance.get('total_nodes', 'N/A')}\n")

            # 节点耗时详情
            node_timings = performance.get('node_timings', {})
            if node_timings:
                f.write("\n### 各阶段耗时\n\n")
                for node_name, elapsed in node_timings.items():
                    f.write(f"- **{node_name}**: {elapsed:.2f}秒\n")
        else:
            f.write("*无性能数据*\n")

        f.write("\n---\n\n")

    def _write_footer(self, f):
        """写入文件尾"""
        f.write("---\n\n")
        f.write(f"*本报告由 TradingAgents AI 系统自动生成*\n\n")
        f.write(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        f.write("\n" + "=" * 80 + "\n")


def export_analysis_result(
    ticker: str,
    trade_date: str,
    state: Dict[str, Any],
    decision: Dict[str, Any],
    execution_log: List[Dict] = None,
    output_dir: str = None
) -> str:
    """
    便捷函数：导出分析结果到文件

    Args:
        ticker: 股票代码
        trade_date: 交易日期
        state: 完整的分析状态
        decision: 最终投资决策
        execution_log: 执行日志（可选）
        output_dir: 输出目录（可选）

    Returns:
        导出文件的路径
    """
    exporter = AnalysisResultExporter(output_dir)
    return exporter.export(ticker, trade_date, state, decision, execution_log)
