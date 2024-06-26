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
from pisameet.process import crawl
from pm2024 import POSTER_FOLDER_PATH, POSTER_RASTER_FOLDER_PATH


PARSER = argparse.ArgumentParser()
PARSER.add_argument('--posters', type=int, nargs='+',
    help='the ids of the posters to be processed')
PARSER.add_argument('--output_folder', type=str, default=POSTER_RASTER_FOLDER_PATH,
    help='output folder for the rasterized png files')
PARSER.add_argument('--target_width', type=int, default=1060,
    help='target width for the output png')
PARSER.add_argument('--intermediate_width', type=int, default=4240,
    help='intermediate width')
PARSER.add_argument('--autocrop', action='store_true')
PARSER.add_argument('--overwrite', action='store_true')


_AUTOCROP_LIST = [1, 23, 29, 60, 66, 87, 88, 100, 110, 111, 114, 116, 129, 139, 184, 189, 191,
    198, 208, 211, 212, 219, 220, 224, 234, 242, 245, 256, 262, 263, 265, 279, 287,
    290, 299, 308, 311, 316, 322, 331, 335, 340, 369, 375, 377, 381, 388, 389, 425, 436,
    437, 471, 479, 488]



def raster_poster(poster_id: int, target_width: int, intermediate_width: int, output_folder: str,
    overwrite: bool = False, autocrop: bool = False):
    """
    """
    poster_name = f'{poster_id:03}'
    input_file_path = os.path.join(POSTER_FOLDER_PATH, f'{poster_name}.pdf')
    output_file_path = os.path.join(output_folder, f'{poster_name}.png')
    if poster_id in _AUTOCROP_LIST:
        autocrop = True
    raster.raster_pdf(input_file_path, output_file_path, target_width,
        intermediate_width, overwrite, autocrop)



if __name__ == '__main__':
    args = PARSER.parse_args()
    if args.posters is None:
        for file_path in crawl(POSTER_FOLDER_PATH):
            file_name = os.path.basename(file_path)
            poster_id = int(file_name.replace('.pdf', ''))
            raster_poster(poster_id, args.target_width, args.intermediate_width,
                args.output_folder, args.overwrite, args.autocrop)
    else:
        for poster_id in args.posters:
            raster_poster(poster_id, args.target_width, args.intermediate_width,
                args.output_folder, args.overwrite, args.autocrop)
