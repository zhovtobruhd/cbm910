import json
import sys

import serial

from cbm910 import CBM910


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

printer = CBM910(serial.Serial(**config))

with open(sys.argv[1], 'rb') as f:
    d = f.read()

printer.write(d)

del printer