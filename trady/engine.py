# -*- coding: utf-8 -*-


class StrategyEngine(object):

    def __init__(self, chart, strategy, method="on_bar_close"):
        """A StrategyEngine runs a given strategy over history or real time data.

        Args:
            chart (Chart): The price chart.
            strategy (Strategy): The strategy to use in this StrategyEngine.
            method (str): One of: "on_bar_close" or "intra_bar".

        """
        self.chart = chart
        self.strategy = strategy
        self.method = method

    def start(self):
        """Start the StrategyEngine

        """
        account = Account()
        strategy = strategy(account)
        for bar in chart:
            strategy.trade(bar)
