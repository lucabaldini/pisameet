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
import glob

from loguru import logger

from pm2024 import PRESENTER_FOLDER_PATH, PRESENTER_CROP_FOLDER_PATH
from pisameet.raster import crop_to_face


PARSER = argparse.ArgumentParser()
PARSER.add_argument('--posters', type=int, nargs='+',
    help='the ids of the posters to be processed')
PARSER.add_argument('--target_height', type=int, default=132,
    help='target height for the output png')
PARSER.add_argument('--overwrite', action='store_true')


def crop_presenter_pic(input_file_path: str, target_height, overwrite: bool = False):
    """Process a single presenter pic.
    """
    candidates = glob.glob(os.path.join(PRESENTER_FOLDER_PATH, f'{poster_id:03}.*'))
    input_file_path = os.path.join(PRESENTER_FOLDER_PATH, candidates[0])
    output_file_path = os.path.join(PRESENTER_CROP_FOLDER_PATH, f'{poster_id:03}.png')
    crop_to_face(input_file_path, output_file_path, target_height, overwrite)




if __name__ == '__main__':
    args = PARSER.parse_args()
    if args.posters is None:
        pass
    else:
        for poster_id in args.posters:
            crop_presenter_pic(poster_id, args.target_height, args.overwrite)
