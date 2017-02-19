# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
import pandas.util.testing as pdt

from trady.chart import Chart



def test_Chart_load_dict():
    data = [
        {
            "date": "2017-10-01",
            "close": 10,
        },
        {
            "date": "2017-10-02",
            "close": 20,
        },
    ]
    chart = Chart()
    chart.load_dict(data)
    assert len(chart.bars) == 2
    assert chart.bars.close[0] == 10
    assert chart.bars.close[1] == 20
    assert chart.bars.index[0] == pd.Timestamp("2017-10-01 00:00:00")
    assert chart.bars.index[1] == pd.Timestamp("2017-10-02 00:00:00")


def test_Chart_load_dict_sets_log_return():
    data = [
        {
            "date": "2017-01-01",
            "close": 10,
        },
        {
            "date": "2017-01-02",
            "close": 20,
        },
        {
            "date": "2017-01-03",
            "close": 15,
        },
    ]
    chart = Chart()
    chart.load_dict(data)
    assert chart.bars.log_return[2] == math.log(15) - math.log(20)
    assert chart.bars.log_return[1] == math.log(20) - math.log(10)
    assert np.isnan(chart.bars.log_return[0])


def test_Chart_load_string():
    data = u"""
Date,Open,High,Low,Close,Volume
2017-02-03,130.98,132.06,130.3,132.06,16760692.0
2017-02-06,131.24,132.85,130.76,130.88,24068306.0
"""
    chart = Chart()
    chart.load_string(data, date_name="Date", columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
    })
    assert len(chart.bars) == 2
    assert chart.bars.index.name == "date"
    from dateutil import parser
    assert chart.bars.index[0].isoformat() == "2017-02-03T00:00:00"
    assert chart.bars.open[0] == 130.98
    assert chart.bars.high[0] == 132.06
    assert chart.bars.low[0] == 130.3
    assert chart.bars.close[0] == 132.06
    assert chart.bars.volume[0] == 16760692.0
    assert chart.bars.index[1].isoformat() == "2017-02-06T00:00:00"
    assert chart.bars.open[1] == 131.24
    assert chart.bars.high[1] == 132.85
    assert chart.bars.low[1] == 130.76
    assert chart.bars.close[1] == 130.88
    assert chart.bars.volume[1] == 24068306.0


def test_Chart_bars_ordered_by_date_descending():
    chart = Chart()
    chart.load_dict([
        {
            "date": "2017-01-01",
            "close": 10,
        },
        {
            "date": "2017-01-02",
            "close": 11,
        },
        {
            "date": "2017-01-03",
            "close": 12,
        },
    ])
    assert chart.bars.index[2] == pd.Timestamp("2017-01-03")
    assert chart.bars.index[1] == pd.Timestamp("2017-01-02")
    assert chart.bars.index[0] == pd.Timestamp("2017-01-01")


def test_Chart_get_volatilities():
    chart = Chart()
    chart.load_dict([
        {
            "date": "2017-01-04",
            "close": 100,
        },
        {
            "date": "2017-01-02",
            "close": 110,
        },
        {
            "date": "2017-01-03",
            "close": 90,
        },
        {
            "date": "2017-01-01",
            "close": 105,
        },
    ])
    volatilities = chart.get_volatilities(delta=3)
    assert np.isnan(volatilities[0])
    assert np.isnan(volatilities[1])
    assert np.isnan(volatilities[2])
    log_returns = [
        math.log(100.0) - math.log(90.0),
        math.log(90.0) - math.log(110.0),
        math.log(110.0) - math.log(105.0),
    ]
    log_returns = map(lambda x: round(x, 6), log_returns)
    mu = sum(log_returns) / 3.0
    standard_dev = math.sqrt(sum(map(lambda x: math.pow(x - mu, 2), log_returns)) / 2.0) * math.sqrt(250)
    assert round(volatilities[3], 4) == round(standard_dev, 4)
