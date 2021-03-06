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

import trady


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
    chart = trady.chart.Chart()
    chart.load_api(symbol)
    return chart.bars.reset_index().to_json(orient="records", date_format="epoch")
