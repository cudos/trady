# -*- coding: utf-8 -*-

import math
import os

from pyramid.view import view_config
from pyramid.renderers import render

from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPFound,
    HTTPNotFound,
)

from trady.chart import Chart


here = os.path.dirname(__file__)


@view_config(route_name="stock-report", renderer="templates/stock-report.jinja2")
def stock_report_view(request):
    symbol = request.params.get("symbol")
    return {
        "symbol": symbol,
    }


@view_config(route_name="chart", renderer="string")
def chart_view(request):
    symbol = request.params.get("symbol")
    chart = Chart()
    chart.load_api(symbol)
    return chart.bars.to_json(orient="records", date_format="iso")
