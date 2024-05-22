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
import PIL.Image

DEFAULT_LOGURU_HANDLER = dict(sink=sys.stderr, colorize=True, format=">>> <level>{message}</level>")
logger.remove()
logger.add(**DEFAULT_LOGURU_HANDLER)

_REFERENCE_DENSITY = 72.



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

def pdf_to_png(input_file_path: str, output_file_path: str, density: float = _REFERENCE_DENSITY,
    compression_level: int = 0) -> str:
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
    logger.info(f'Converting {input_file_path} to {output_file_path} @{density:.3f} dpi...')
    subprocess.run(['convert', '-density', f'{density}', '-define',
        f'png:compression-level={compression_level}', input_file_path, output_file_path],
        check=True)
    return output_file_path

def _resize_image(img, width, height, output_file_path=None, resample=PIL.Image.LANCZOS,
    reducing_gap=3., compression_level=6):
    """Base function to resize an image.
    """
    w, h = img.size
    logger.info(f'Resizing image ({w}, {h}) -> ({width}, {height})...')
    img = img.resize((width, height), resample, None, reducing_gap)
    if output_file_path is not None:
        logger.info(f'Saving image to {output_file_path}...')
        img.save(output_file_path, compress_level=compression_level)

def png_resize_to_width(input_file_path: str, output_file_path: str, width: int, **kwargs):
    """Resize an image to the target width.
    """
    with PIL.Image.open(input_file_path) as img:
        w, h = img.size
        height = round(width / w * h)
        _resize_image(img, width, height, output_file_path, **kwargs)

def png_resize_to_height(input_file_path: str, output_file_path: str, height: int, **kwargs):
    """Resize an image to the target height.
    """
    with PIL.Image.open(input_file_path) as img:
        w, h = img.size
        width = round(height / h * w)
        _resize_image(img, width, height, output_file_path, **kwargs)

def raster_pdf(input_file_path: str, output_file_path: str, target_width: int,
    intermediate_width: int = None) -> str:
    """Raster a pdf.
    """
    logger.info(f'Rastering {input_file_path}...')
    original_width, original_height = pdf_page_size(input_file_path)
    # Are we skipping the intermediate rastering?
    if intermediate_width is None or intermediate_width <= target_width:
        logger.debug('Skipping intermediate rastering...')
        density = target_width / original_width * _REFERENCE_DENSITY
        return pdf_to_png(input_file_path, output_file_path, density)
    logger.debug('Performing intermediate rastering...')
    density = intermediate_width / original_width * _REFERENCE_DENSITY
    file_path = pdf_to_png(input_file_path, output_file_path, density)
    logger.debug('Resizing to target width...')
    return png_resize_to_width(file_path, file_path, target_width)
