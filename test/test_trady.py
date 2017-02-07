# -*- coding: utf-8 -*-

import trady


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
