# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pandas.util.testing as pdt

import trady



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
    chart = trady.Chart()
    chart.load_dict(data)
    assert len(chart.bars) == 2
    assert chart.bars.close[0] == 10
    assert chart.bars.close[1] == 20
    assert chart.bars.index[0] == pd.Timestamp("2017-10-01 00:00:00")
    assert chart.bars.index[1] == pd.Timestamp("2017-10-02 00:00:00")


def test_Chart_load_dict_sets_daily_return():
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
    chart = trady.Chart()
    chart.load_dict(data)
    pdt.assert_series_equal(
        chart.bars.daily_return,
        pd.Series([np.nan, 1.0, -0.25], index=chart.bars.index, name="daily_return")
    )


def test_Chart_load_string():
    data = u"""
Date,Open,High,Low,Close,Volume
2017-02-03,130.98,132.06,130.3,132.06,16760692.0
2017-02-06,131.24,132.85,130.76,130.88,24068306.0
"""
    chart = trady.Chart()
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


def test_Chart_get_anual_volatilities():
    chart = trady.Chart()
    chart.load_dict([
        {
            "date": "2017-01-01",
            "close": 100,
        },
        {
            "date": "2017-01-02",
            "close": 120,
        },
        {
            "date": "2017-01-03",
            "close": 114,
        },
        {
            "date": "2018-01-01",
            "close": 114,
        },
        {
            "date": "2018-01-02",
            "close": 125.4,
        },
    ])
    volatilities = chart.get_anual_volatilities()
    pdt.assert_series_equal(volatilities, pd.Series([0.176777, 0.070711], index=[2017, 2018], name="volatility"))
