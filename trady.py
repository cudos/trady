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
import io
import os
import shutil
import subprocess
import sys
import tempfile

import jinja2
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import pdfkit
import requests

import trady.strategies as strategies


def main():
    parser = argparse.ArgumentParser(
        description="trady - analyse algorithmic trading systems"
    )
    parser.add_argument("--symbol", type=str, required=True, help="the symbol identifying the paper to use in the simulation")
    parser.add_argument("--strategy", type=str, required=True, help="the strategy to use in the simulation process")
    args = parser.parse_args()

    if not os.path.exists("simulations"):
        os.mkdir("simulations")

    if os.path.exists("last_simulation"):
        with open("last_simulation", "r") as last_simulation:
            last_simulation_id = int(last_simulation.read())
    else:
        last_simulation_id = 0

    current_simulation_id = last_simulation_id + 1

    output_dir = os.path.join("simulations", str(current_simulation_id))
    if os.path.exists(output_dir):
        print >> sys.stderr, "Error: simulation output directory '{}' already exists".format(output_dir)
        sys.exit(1)

    # Create temporary output directory
    output_dir_tmp = tempfile.mkdtemp()

    # Get strategy module
    print "Load strategy module {}...".format(args.strategy)
    strategy_cls = getattr(strategies, args.strategy)
    if not strategy_cls:
        print >> sys.stderr, "Error: strategy '{}' does not exist".format(args.strategy)
        sys.exit(1)

    strategy = strategy_cls()

    template_vars = {
        "title": "some title",
        "simulation_id": current_simulation_id,
        "strategy": strategy,
        "symbol": args.symbol,
    }

    params = {"s": args.symbol}
    url = "http://ichart.finance.yahoo.com/table.csv"
    print "Get historical prices from yahoo finance for symbol {}...".format(args.symbol)
    r = requests.get(url, params=params)
    df = pd.read_csv(io.StringIO(r.text))
    print "Got {} records".format(df.shape[0])
    template_vars["source_url"] = r.url
    template_vars["raw_description"] = df.describe().to_html()
    template_vars["raw_values"] = df.to_html()

    # # Write pdf report
    # with PdfPages("foo.pdf") as pdf:
    #     plt.figure(figsize=(3, 3))
    #     plt.plot(range(7), [3, 1, 4, 2, 5, 5, 2], "r-o")
    #     plt.title("Page One")
    #     pdf.savefig()
    #     plt.close()

    # Render report as html
    print "Render report as html..."
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates"))
    template = env.get_template("report.html")
    html_out = template.render(template_vars)
    with open(os.path.join(output_dir_tmp, "report.html"), "w") as html:
        html.write(html_out)

    # Render report as pdf
    print "Render report as pdf..."
    pdfkit.from_string(html_out, os.path.join(output_dir_tmp, "report.pdf"), css=os.path.join("templates", "style.css"))

    # Increase last_simulation counter by 1
    with open("last_simulation", "w") as last_simulation:
        last_simulation.write(str(current_simulation_id))

    # Copy temp output directory to its final destination
    shutil.copytree(output_dir_tmp, output_dir)
    shutil.rmtree(output_dir_tmp)

    # Display output directory
    subprocess.call(["tree", output_dir])
    subprocess.call(["evince", os.path.join(output_dir, "report.pdf")])

    return 0


if __name__ == "__main__":
    sys.exit(main())
