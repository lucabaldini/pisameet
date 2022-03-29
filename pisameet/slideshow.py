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
from __init__ import logger

PARSER = argparse.ArgumentParser()
PARSER.add_argument('cfgfile', type=str,
    help='path to the input excel configuration file')
PARSER.add_argument('--advance', type=float, default=30.,
    help='the time interval for the slide show transition [s]')
PARSER.add_argument('--pause', type=float, default=120.,
    help='the time interval for the slide show pause [s]')
PARSER.add_argument('--fading', action='store_true',
    help='enable the fading effect between posters')
PARSER.add_argument('--no-fading', action='store_false',
    help='disable the fading effect between posters')
PARSER.set_defaults(fading=False)
PARSER.add_argument('--mode', type=str, default='maximize', choices=SlideShow.VALID_MODES,
    help='display geometry')
PARSER.add_argument('--poster-width', type=int, default=None,
    help='width of the poster display (taken from the screen size by default)')
PARSER.add_argument('--header-height', type=int, default=250,
    help='height of the poster header')
PARSER.add_argument('--portrait-height', type=int, default=120,
    help='height of the presenter portraits and QR codes')
PARSER.add_argument('--background', type=str, default='white',
    help='background color')


if __name__ == '__main__':
    args = PARSER.parse_args()
    app = QApplication(sys.argv)
    kwargs = args.__dict__
    # Determine the appropriate poster width from the screen size unless this is
    # explicitly overridden via command-line options.
    if kwargs.get('poster_width') is None:
        poster_width = app.screens()[0].size().width() - 20
        logger.info('Setting posted width to %d (based on the screen size)', poster_width)
        kwargs['poster_width'] = poster_width
    slideshow = SlideShow(**kwargs)
    sys.exit(app.exec_())
