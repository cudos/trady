# -*- coding: utf-8 -*-
# Copyright (C) 2017  Jens Hoffmann <xmcpam@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
import pandas as pd
import requests
import matplotlib.pyplot as plt
import math


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


class Account(object):
    """The portfolio account.

    Args:
        cash (float): Total amount of cash available for trading
            stocks with. A negative cash value indicates that you are
            borrowing from your margin account.
        margin (float): ...

    """
    def __init__(self, cash, commission, day=0, margin_rate=None):
        self.cash = float(cash)
        self.day = day
        self.margin_rate = float(margin_rate)
        self.commission = commission
        self.starting_account_value = self.account_value

    def trade_stock(self):
        pass

    def trade_option(self):
        pass

    def short_stock(self):
        pass

    def increase_day(self):
        self.day += 1

    @property
    def buying_power(self):
        """The total value of your cash and margin accounts that can be used
        to trade stocks. Negative buying power indicates that no
        further trading can be performed and that margin call will
        occur.

        """
        return self.cash + (self.market_value_of_stocks * self.margin_rate) - (self.market_value_of_short_stocks * (1.0 + self.margin_rate))

    @property
    def account_value(self):
        """Your portfolio's current value.

        """
        return self.cash + self.value_of_stocks + self.value_of_options - self.value_of_short_stocks

    @property
    def market_value_of_stocks(self):
        return 0

    @property
    def market_value_of_options(self):
        return 0

    @property
    def market_value_of_short_stocks(self):
        return 0

    @property
    def annual_return(self):
        """Amount of returns generated if your current rate of returns were
        extrapolated for an entire year.

        """
        return math.pow(self.account_value / self.starting_account_value, 365.0 / self.day) - 1

    def set_stop_loss(self, stop_amount):
        """Set a safety stop loss for both long and short positions.

        Args:
            stop_amount (float): The safety stop in dollar.

        """
        pass

    def set_profit_target(self, profit_amount):
        """Set a profit target for both long and short positions.

        Args:
            profit_amount (float): The profit target in dollar.

        """
        pass

    def market_position(self, n):
        """Returns whether the strategy is currently flat, short, or long on
        the current bar or for `n` closed positions ago.

        Returns: int: The market position. Values are: -1 for a short
            position. 1 for a long position. 0 for flat (no position).

        """
        pass


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


class Chart(object):

    def __init__(self):
        self.bars = None

    def load_dict(self, bars):
        """Load bar records from a python list of of dictionaries where each
        dictionary describes a record.

        """
        self.bars = pd.DataFrame(bars)
        self.bars["date"] = pd.to_datetime(self.bars["date"])
        self._finalize_bars()

    def load_string(self, string, date_name="date", columns=None):
        """Load chart values from a given string as csv.

        """
        self.bars = pd.read_csv(io.StringIO(string), parse_dates=[date_name])
        if columns:
            self.bars.rename(index=str, columns=columns, inplace=True)
        self._finalize_bars()

    def load_api(self, symbol):
        """Load chart values from an API

        """
        self.symbol = symbol
        params = {"s": self.symbol}
        url = "http://ichart.finance.yahoo.com/table.csv"
        r = requests.get(url, params=params)
        self.source_url = r.url
        self.load_string(r.text, date_name="Date", columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Adj Close": "adj close"
        })

    def get_anual_volatilities(self):
        """Return a DataFrame containing anual volatilities.

        """
        if self.bars is None:
            return None

        return self.bars["return"].groupby(self.bars.index.year).std().rename("volatility") * math.sqrt(250.0)

    def get_anual_returns(self):
        if self.bars is None:
            return None

        volatilities = self.get_anual_volatilities()
        mean_returns = self.bars["return"].groupby(self.bars.index.year).mean().rename("return mean")
        return pd.concat([mean_returns, volatilities], axis=1)

    def plot_prices(self, output):
        fig = plt.figure()
        plt.title("Price history {}".format(self.symbol))
        self.bars.close.plot(figsize=(10, 4))
        plt.xlabel("Year")
        plt.ylabel("Price")
        plt.grid()
        plt.tight_layout()
        plt.savefig(output)

    def plot_anual_return_distributions(self, output):
        plt.figure()
        self.bars["return"].hist(by=self.bars.index.year)
        plt.grid()
        plt.savefig(output)

    def write_prices_to_file(self, output_file):
        with open(output_file, "w") as fp:
            fp.write(self.raw_prices)

    @property
    def description_as_html(self):
        return self.bars.describe().to_html()

    @property
    def first_date(self):
        return self.bars.index.min()

    @property
    def last_date(self):
        return self.bars.index.max()

    @property
    def number_of_values(self):
        return len(self.bars.index)

    def get_prices(self):
        return self.bars.iterrows()

    def _finalize_bars(self):
        self.bars = self.bars.sort_values(by="date")
        self.bars.set_index("date", inplace=True)
        self.bars["return"] = (self.bars.close - self.bars.close.shift()) / self.bars.close.shift()


class BaseStrategy(object):
    """Base class for all strategies in trady.strategies

    """
    def __init__(self, account):
        self.account = account
