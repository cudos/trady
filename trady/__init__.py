# -*- coding: utf-8 -*-

import pandas as pd
from pyramid.config import Configurator


def main(global_config, **settings):  # pragma: no cover
    """This function returns a Pyramid WSGI application.

    """
    config = Configurator(
        settings=settings
    )
    config.include("pyramid_jinja2")
    config.add_static_view("static", "trady:static")
    config.add_static_view("assets", "trady:assets")
    config.include(addroutes)
    config.scan()

    return config.make_wsgi_app()


def addroutes(config):
    config.add_route("stock-report", "/stock-report")
    config.add_route("chart", "/chart")
