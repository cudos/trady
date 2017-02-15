# -*- coding: utf-8 -*-



class Simulation(object):
    """A Simulation is responsible for initializing a Chart, an Account,
    a Strategy and a StrategyEngine and let the StrategyEngine run
    over the given Chart.

    """
    def __init__(self, strategy_cls, chart, initial_equity):
        self.strategy_cls = strategy_cls
        self.chart = chart
        self.initial_equity = initial_equity

    def start(self):
        engine = StrategyEngine(strategy_cls)
