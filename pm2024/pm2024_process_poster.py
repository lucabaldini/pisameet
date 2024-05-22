#!/usr/bin/env python3
#
# Copyright (C) 2024, luca.baldini@pi.infn.it
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

"""Process the local copies of the poster files.
"""

import argparse
import os

from pisameet import raster
from pm2024 import POSTER_ORIGINAL_FOLDER_PATH, POSTER_IMAGE_FOLDER_PATH


PARSER = argparse.ArgumentParser()
PARSER.add_argument('posters', type=int, nargs='+',
    help='the ids of the posters to be processed')
PARSER.add_argument('--width', type=int, default=2120,
    help='target width for the output png')
PARSER.add_argument('--intermediate_min_size', type=int, default=6360,
    help='intermediate minimum size')


def raster_poster(poster_id: int, target_width: int, intermediate_min_size: int):
    """
    """
    input_file_path = os.path.join(POSTER_ORIGINAL_FOLDER_PATH, f'{poster_id:03}.pdf')
    output_file_path = os.path.join(POSTER_IMAGE_FOLDER_PATH, f'{poster_id:03}.png')
    raster.raster_pdf(input_file_path, output_file_path, target_width, intermediate_min_size)



if __name__ == '__main__':
    args = PARSER.parse_args()
    for poster_id in args.posters:
        raster_poster(poster_id, args.width, args.intermediate_min_size)
