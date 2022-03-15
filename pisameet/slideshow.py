#!/usr/bin/env python3
#
# Copyright (C) 2021--2022, luca.baldini@pi.infn.it
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Main slideshow application.
"""

import argparse
import sys

from PyQt5.QtWidgets import QApplication

from gui import SlideShow

PARSER = argparse.ArgumentParser()
PARSER.add_argument('cfgfile', type=str,
    help='path to the input excel configuration file')
PARSER.add_argument('--advance', type=float, default=SlideShow.DEFAULT_ADVANCE_INTERVAL,
    help='the time interval for the slide show transition [s]')
PARSER.add_argument('--pause', type=float, default=SlideShow.DEFAULT_PAUSE_INTERVAL,
    help='the time interval for the slide show pause [s]')
PARSER.add_argument('--geometry', type=str, default='default', choices=SlideShow.VALID_GEOMETRIES,
    help='display geometry')
PARSER.add_argument('--poster-width', type=int, default=600,
    help='width of the poster display')
PARSER.add_argument('--header-height', type=int, default=200,
    help='height of the poster header')
PARSER.add_argument('--portrait-height', type=int, default=120,
    help='height of the presenter portraits and QR codes')
PARSER.add_argument('--footer-height', type=int, default=40,
    help='height of the poster footer')
PARSER.add_argument('--background', type=str, default='white',
    help='background color')


if __name__ == '__main__':
    args = PARSER.parse_args()
    app = QApplication(sys.argv)
    slideshow = SlideShow('posters', **args.__dict__)
    sys.exit(app.exec_())
