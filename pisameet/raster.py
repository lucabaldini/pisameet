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

"""Rasterization tools.
"""

import os
import subprocess
import sys

from loguru import logger
import pdfrw
import PIL

DEFAULT_LOGURU_HANDLER = dict(sink=sys.stderr, colorize=True, format=">>> <level>{message}</level>")
logger.remove()
logger.add(**DEFAULT_LOGURU_HANDLER)


def pdf_page_size(file_path: str, page_number: int=0) -> tuple[int, int]:
    """Return the page size for a given page of a given pdf document.

    Arguments
    ---------
    file_path : str
        The path to the input pdf file.

    page_number : int
        The target page number (starting from zero).
    """
    if not file_path.endswith('.pdf'):
        raise RuntimeError(f'{file_path} not a pdf file?')
    logger.debug(f'Retrieving page {page_number} size from {file_path}...')
    document = pdfrw.PdfReader(file_path)
    page = document.pages[page_number]
    # This is a list of strings, e.g., ['0', '0', '1683.72', '2383.92']...
    bbox = page.MediaBox or page.Parent.MediaBox
    # ... which we convert to a list of float, e.g., [0, 0, 1683.72, 2383.92]
    bbox = [float(val) for val in bbox]
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    logger.debug(f'Page size: ({width}, {height}).')
    return width, height

def pdf_to_png(input_file_path: str, output_file_path: str, density: float = 72.) -> str:
    """Convert a .pdf file to a .png file using imagemagick convert under the hood.

    See https://imagemagick.org/script/command-line-options.php for some basic
    information about convert's internals.

    Arguments
    ---------
    input_file_path : str
        The path to the input pdf file.

    output_file_path : str
        The path to the output rasterized file.

    density : int
        The density (in dpi) to be passed to convert.
    """
    if not input_file_path.endswith('.pdf'):
        raise RuntimeError(f'{input_file_path} not a pdf file?')
    logger.info(f'Converting {input_file_path} to {output_file_path} @{density} dpi...')
    subprocess.run(['convert', '-density', f'{density}', input_file_path, output_file_path], check=True)
    return output_file_path

def raster_pdf(input_file_path: str, output_file_path: str, width: int, intermediate_size: int) -> str:
    """Raster a pdf.
    """
    pass



if __name__ == '__main__':
    print(pdf_to_png('/data/work/pisameet/pm2024/poster_original/003.pdf', '/data/temp/test.png'))
