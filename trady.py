#! /usr/bin/env python
# -*- coding: utf-8 -*-
# trady - analyse algorithmic trading systems
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

import argparse
import inspect
import io
import os
import shutil
import subprocess
import sys
import tempfile

import jinja2
import matplotlib.pyplot as plt
import pandas as pd
import pdfkit
import requests

import trady
import trady.strategies as strategies


def main():
    # Setup command line parser
    parser = argparse.ArgumentParser(
        description="trady - analyse algorithmic trading systems"
    )
    parser.add_argument("--symbol", help="the symbol identifying the paper to use in the simulation")
    parser.add_argument("--strategy", help="the strategy to use in the simulation process")
    parser.add_argument("--equity", type=float, default=5000.0, help="the equity to start the simulation with (default: 5000.0)")
    parser.add_argument("--show-report", help="display report with given report id")
    parser.add_argument("--list-reports", action="store_true", help="list existing reports")
    parser.add_argument("--list-strategies", action="store_true", help="list existing strategies")
    args = parser.parse_args()

    # Setup simulations base directory
    if not os.path.exists("simulations"):
        os.mkdir("simulations")

    # List available reports when requested
    if args.list_reports:
        simulations = sorted([int(x) for x in os.listdir("simulations")])
        for simulation in simulations:
            print simulation
        sys.exit(0)

    # List available strategies when requested
    if args.list_strategies:
        for name, obj in inspect.getmembers(trady.strategies):
            if inspect.isclass(obj):
                print obj.__name__, "-", " ".join(obj.description.split())
        sys.exit(0)

    # Display report with given report id
    if args.show_report:
        report_path = os.path.join("simulations", args.show_report, "report.pdf")
        if not os.path.exists(report_path):
            print >> sys.stderr, "Report with ID {} does not exist. See {} --list-reports for a list of available reports.".format(args.show_report, sys.argv[0])
            sys.exit(1)
        subprocess.Popen(["see", report_path])
        sys.exit(0)

    # Setup simulations counter
    if os.path.exists("last_simulation"):
        with open("last_simulation", "r") as last_simulation:
            last_simulation_id = int(last_simulation.read())
    else:
        last_simulation_id = 0
    current_simulation_id = last_simulation_id + 1

    # Setup output directories
    output_dir = os.path.join("simulations", str(current_simulation_id))
    if os.path.exists(output_dir):
        print >> sys.stderr, "Error: simulation output directory '{}' already exists".format(output_dir)
        sys.exit(1)
    output_dir_tmp = tempfile.mkdtemp()
    chart_dir = os.path.join(output_dir_tmp, "charts")
    os.mkdir(chart_dir)

    # Get strategy module
    print "Load strategy module {}...".format(args.strategy)
    strategy_cls = getattr(strategies, args.strategy, None)
    if not strategy_cls:
        print >> sys.stderr, "Error: strategy does not exist: {}".format(args.strategy)
        print >> sys.stderr, "List all strategies with --list-strategies"
        sys.exit(1)

    if not strategy_cls:
        print >> sys.stderr, "Error: strategy '{}' does not exist".format(args.strategy)
        sys.exit(1)

    # Setup variables to be used when rendering the report
    template_vars = {
        "title": "some title",
        "simulation_id": current_simulation_id,
        "strategy": strategy_cls,
        "symbol": args.symbol,
        "trady_revision": subprocess.check_output(["git", "describe", "--always"]).strip()
    }

    # Get price history data for the given symbol
    print "Get historical prices for symbol {}...".format(args.symbol)
    chart = Chart(
        symbol=args.symbol,
    )
    chart.write_prices_to_file(os.path.join(output_dir_tmp, "all-prices.csv"))
    all_prices_chart = os.path.join(chart_dir, "all-prices-chart.png")
    chart.plot_prices(all_prices_chart)
    template_vars["all_prices_chart"] = all_prices_chart
    template_vars["chart"] = chart

    # Run the simulation
    print "Run simulation..."
    simulation = trady.Simulation(strategy_cls=strategy_cls, chart=chart, initial_equity=args.equity)
    simulation.start()
    print simulation.get_summary()

    # Render report as html
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
    template = env.get_template("report.html")
    html_out = template.render(template_vars)

    # Render report as pdf
    print "Render report {}...".format(os.path.join(output_dir, "report.pdf"))
    pdfkit.from_string(html_out, os.path.join(output_dir_tmp, "report.pdf"), css=os.path.join("templates", "style.css"))

    # Increase last_simulation counter by 1
    with open("last_simulation", "w") as last_simulation:
        last_simulation.write(str(current_simulation_id))

    # Copy temp output directory to its final destination
    shutil.copytree(output_dir_tmp, output_dir)
    shutil.rmtree(output_dir_tmp)

    # Display output directory
    subprocess.call(["tree", output_dir])
    subprocess.Popen(["see", os.path.join(output_dir, "report.pdf")])

    return 0


if __name__ == "__main__":
    sys.exit(main())
