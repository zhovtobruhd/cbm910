# Copyright 2026 Dmytro Zhovtobriukh
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import click
import serial

from cbm910 import CBM910, CodePage


@click.group()
def cli():
    pass


@cli.command('print')
@click.option('--file', type=click.Path(), help='File to print')
@click.option('--text', type=click.STRING, help='Text to print')
@click.option('--config', type=click.Path(), default="config.json",
              help='Serial Port Configuration File')
@click.option('--codepage', type=click.Choice(CodePage.names()),
              help='Code Page Selection')
@click.option('--feed-paper', type=click.IntRange(4, 255), default=None,
              help='Feed paper after printing')
def cmd_print(file, text, codepage, config, feed_paper):
    """ Prints the file or text provided """

    if file and text:
        click.echo("'--file' and '--text' are mutually exclusive")
        raise SystemExit(1)

    with open(config, "r", encoding="utf-8") as f:
        cfg= json.load(f)

    if file:
        with open(file, "rb") as f:
            payload = f.read()
    elif text:
        payload = text.encode("utf-8")
    else:
        click.echo("No file or text provided")
        raise SystemExit(1)

    printer = CBM910(serial.Serial(**cfg))

    if codepage:
        printer.set_code_page(CodePage(codepage))

    printer.write(payload)

    if feed_paper:
        printer.feed_paper(feed_paper)

    del printer


if __name__=="__main__":
    cli()
