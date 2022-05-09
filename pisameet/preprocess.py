#
# Copyright (C) 2021, luca.baldini@pi.infn.it
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

"""Pre-processing tools.
"""

import os
import subprocess

from pisameet import logger
from pisameet.qrcode_ import generate_qrcode


def crawl(folder_path: str, file_type: str = '.pdf', filter_pattern: str = None) -> list:
    """Crawl a given folder recursively and return a list of all the files of
    a given type matching a given pattern.

    Arguments
    ---------
    folder_path : str
        The path to the root folder to be recursively crawled.

    file_type : str
        The file extension, including the dot (e.g., '.pdf')

    filter_pattern : str
        An optional filtering pattern---if not None, only the files containing
        the pattern in the name are retained.

    Return
    ------
    A list of absolute file paths.
    """
    file_list = []
    for root, _, files in os.walk(folder_path):
        file_list += [os.path.join(root, file) for file in files if file.endswith(file_type)]
    file_list.sort()
    if filter_pattern is not None:
        file_list = [file_path for file_path in file_list \
            if filter_pattern in os.path.basename(file_path)]
    return file_list


def pdf_to_png(input_file_path: str, output_folder_path) -> str:
    """Convert a .pdf file to a .png file.
    """
    assert input_file_path.endswith('.pdf')
    file_name = os.path.basename(input_file_path).replace('.pdf', '.png')
    output_file_path = os.path.join(output_folder_path, file_name)
    print('Converting %s to %s...' % (input_file_path, output_file_path))
    subprocess.run(['convert', input_file_path, output_file_path], check=True)
    return output_file_path

def generate_qr_codes(folder_path : str, output_folder_path : str):
    """Generate all the QR codes.
    """
    for file_path in crawl(folder_path):
        poster_id = os.path.basename(file_path).split('-')[0]
        file_name = f'{poster_id}-qrcode.png'
        qrcode_path = os.path.join(output_folder_path, file_name)
        logger.info('Writing QR-code to %s...', qrcode_path)
        generate_qrcode(file_path, qrcode_path)

def preprocess_posters(folder_path : str, output_folder_path : str):
    """Save png versions of the posters.
    """
    for file_path in crawl(folder_path):
        pdf_to_png(file_path, output_folder_path)



if __name__ == '__main__':
    preprocess_posters('pm2022/poster_original', 'pm2022/poster_images')
    generate_qr_codes('pm2022/poster_original', 'pm2022/qrcodes')
