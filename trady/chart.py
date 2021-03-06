# -*- coding: utf-8 -*-

import io
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests


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
            self.bars.rename(index=int, columns=columns, inplace=True)
        self._finalize_bars()

    def load_api(self, symbol):
        """Load chart values from an API

        """
        self.symbol = symbol
        params = {"s": self.symbol}
        url = "http://ichart.finance.yahoo.com/table.csv"
        r = requests.get(url, params=params)
        self.source_url = r.url
        if r.status_code != 200:
            return
        self.load_string(r.text, date_name="Date", columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Adj Close": "adj close"
        })

    def get_volatilities(self, delta):
        """Return a DataFrame containing anual volatilities.

        """
        values = []
        for index, row in self.bars.iterrows():
            offset = self.bars.index.get_loc(index)
            if offset < delta:
                volatility = None
            else:
                volatility = self.bars.iloc[offset-delta+1:offset+1].log_return.std() * math.sqrt(250)
            values.append(volatility)

        return pd.Series(values, index=self.bars.index)


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
        self.bars.sort_values(by="date", inplace=True, ascending=True)
        self.bars.set_index("date", inplace=True)
        self.bars.index.name = "date"
        self.bars["pct_return"] = (self.bars.close - self.bars.close.shift()) / self.bars.close.shift()
        self.bars["log_return"] = np.log(self.bars.close) - np.log(self.bars.close.shift())
        # Assign 30, 60 and 90 day volatilities
        self.bars = self.bars.assign(volatility_30d=self.get_volatilities(delta=30))
        self.bars = self.bars.assign(volatility_60d=self.get_volatilities(delta=60))
        self.bars = self.bars.assign(volatility_90d=self.get_volatilities(delta=90))
