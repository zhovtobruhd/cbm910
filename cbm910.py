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

""" CBM910 Dot-Matrix Printer Control """

from enum import Enum
import struct

import serial


class CodePage(Enum):
    """ Code Page Selection for CBM910"""
    PC437 = b'\x00'                   # PC437 (USA, Standard Europe)
    KATAKANA = b'\x01'                # Katakana
    PC858 = b'\x02'                   # PC858 (Multilingual)
    PC860 = b'\x03'                   # PC860 (Portuguese)
    PC863 = b'\x04'                   # PC863 (Canadian-French)
    PC865 = b'\x05'                   # PC865 (Nordic)
    PC852 = b'\x06'                   # PC852 (Eastern Europe)
    PC866 = b'\x07'                   # PC866 (Russian)
    PC857 = b'\x08'                   # PC857 (Turkish)
    WPC1252 = b'\x09'                 # WPC1252 (Windows Latin1)
    PC864 = b'\x0a'                   # PC864 (Arabic)
    PC869 = b'\x0b'                   # PC869 (Greek)
    E910_JP = b'\xfd'                 # 910 Emulation (Japan)
    E910_INT = b'\xfe'                # ASCII + 910 Emulation (International)
    CUSTOM = b'\xff'

    @classmethod
    def names(cls):
        return cls._member_names_


class ControlCode(Enum):
    """ Control Codes for CBM910"""
    LF = b'\x0a'                      # Line feed after print
    CR = b'\x0d'                      # Carriage return and line feed
    SI = b'\x0f'                      # Normal size character
    SO = b'\x0e'                      # Double width character
    US = b'\x1f'                      # Normal size character
    RS = b'\x1e'                      # Double width character
    CAN = b'\x18'                     # Cancel data
    DC2 = b'\x12'                     # Inverted character
    DC1 = b'\x11'                     # Initialize
    FD_PAPER = b'\x1b\x42'            # Feed paper continuously
    SEL_INTL_CHR = b'\x1b\x52'        # Select international character
    SEL_CODE_PAGE = b'\x1b\x74'       # Select code page
    REG_SENTENCE = b'\x1b\x2f'        # Register sentence
    PRT_REGD_CHRS = b'\x1b\x21'       # Print registered characters
    REG_USR_CHR = b'\x1b\x26'         # Register user-defined character
    EN_REGD_CHRS = b'\x1b\x25'        # Enable/Disable registered characters
    PRT_BIT_IMG = b'\x1b\x4b'         # Print bit image
    SET_DBL_H_W_CHR = b'\x1c\x57\x01' # Double height and width character
    CLR_DBL_H_W_CHR = b'\x1c\x57\x00' # Clear double height and width character


class CBM910:
    """ Class for working with CBM910 dot-matrix printer"""

    def __init__(self, ser: serial.Serial):
        self._ser = ser
        self._inverted = False
        self._enlarged = False
        self.initialize()

    def __del__(self):
        self.flush()
        self._ser.close()

    def cancel_data(self):
        """ Cancels data """
        self.write(ControlCode.CAN.value)
        self.flush()

    def disable_enlarge(self):
        """ Disables enlarged (double height and width) character printing """
        if self.enlarged:
            self.write(ControlCode.CLR_DBL_H_W_CHR.value)
            self.flush()
            self._enlarged = False

    def double_width(self):
        """ Enables double width character printing """
        self.write(ControlCode.SO.value)
        self.flush()

    def single_width(self):
        """ Enables single width character printing """
        self.write(ControlCode.SI.value)
        self.flush()

    def enable_enlarge(self):
        """ Enables enlarged (double height and width) character printing """
        if not self.enlarged:
            self.write(ControlCode.SET_DBL_H_W_CHR.value)
            self.flush()
            self._enlarged = True

    def feed_paper(self, n: int):
        """ Feed paper continuously """
        assert 4 <= n <= 255, "'n' must be between 4 and 255"
        self.write(ControlCode.FD_PAPER.value + struct.pack('<B', n))

    def initialize(self):
        """ Sends initialization command """
        self.write(ControlCode.DC1.value)
        self.flush()

    def invert(self):
        """ Inverts character printing """
        self.write(ControlCode.DC2.value)
        self.flush()
        self._inverted = True

    def print_bit_image(self, n1, n2, n3):
        """ Prints bit image """
        assert 1 <= n1 <= 18, "'n1' must be between 1 and 18"
        assert 0 <= n2 <= 255, "'n2' must be between 0 and 255"
        assert 0 <= n3 <= 1, "'n3' must be between 0 and 1"
        self.write(
            ControlCode.PRT_BIT_IMG.value + struct.pack('<BBB', n1, n2, n3)
        )

    def set_inverted(self):
        """ Sets inverted character printing """
        if not self.inverted:
            self.invert()

    def set_non_inverted(self):
        """ Sets non-inverted character printing """
        if self.inverted:
            self.invert()

    def set_code_page(self, code_page: CodePage):
        """ Selects code page """
        self.write(ControlCode.SEL_CODE_PAGE.value + code_page.value)
        self.flush()

    def flush(self):
        """ Flushes command """
        self._ser.flush()

    def write(self, data: bytes):
        """ Writes data to serial """
        self._ser.write(data)

    @property
    def inverted(self):
        """ Returns whether inverted character printing is enabled """
        return self._inverted

    @property
    def enlarged(self):
        """
        Returns whether enlarged (double height and width)
        character printing is enabled
        """
        return self._enlarged
