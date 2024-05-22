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

import cv2
import PIL
from PIL import Image
import pdfrw

from pisameet import logger, PISAMEET_DATA
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



def _resize_image(img, width, height, output_file_path=None, resample=Image.LANCZOS, reducing_gap=3.):
    """Base function to resize an image.
    """
    w, h = img.size
    logger.info('Resizing image (%d, %d) -> (%d, %d)...', w, h, width, height)
    img = img.resize((width, height), resample, None, reducing_gap)
    if output_file_path is not None:
        logger.info('Saving image to %s...', output_file_path)
        img.save(output_file_path)


def resize_image_to_width(file_path, width: int, output_folder_path, **kwargs):
    """Resize an image to the target width.
    """
    with Image.open(file_path) as img:
        w, h = img.size
        height = round(width / w * h)
        file_name = os.path.basename(file_path)
        dest = os.path.join(output_folder_path, f'{file_name.split(".")[0]}.png')
        _resize_image(img, width, height, dest, **kwargs)


def resize_image_to_height(file_path, height: int, output_folder_path, **kwargs):
    """Resize an image to the target height.
    """
    with Image.open(file_path) as img:
        w, h = img.size
        width = round(height / h * w)
        file_name = os.path.basename(file_path)
        dest = os.path.join(output_folder_path, f'{file_name.split(".")[0]}.png')
        _resize_image(img, width, height, dest, **kwargs)


HAARCASCADE_FILE_PATH = os.path.join(PISAMEET_DATA, 'haarcascade_frontalface_default.xml')


def face_bbox(file_path, min_frac_size: float = 0.15, padding=1.85):
    """Run a simple opencv face detection and return the proper bounding box for
    cropping the input image.

    This is returning an approximately square (modulo 1 pixel possible difference
    between the two sides) bounding box containing the face.
    """
    logger.info('Running face detection on %s...', file_path)
    # Run opencv and find the face.
    cascade = cv2.CascadeClassifier(HAARCASCADE_FILE_PATH)
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape
    min_size = round(width * min_frac_size), round(height * min_frac_size)
    faces = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=min_size)
    if len(faces) == 0:
        logger.warning('No candidate face found, returning dummy bounding box...')
        x0, y0 = width // 2, height // 2
        half_side = round(0.5 * min(width, height))
        return (x0 - half_side, y0 - half_side, x0 + half_side, y0 + half_side)
    logger.info('%d candidate bounding boxes found...', len(faces))
    x, y, w, h = faces[-1]
    # Calculate the starting center and size.
    x0, y0 = x + w // 2, y + h // 2
    half_side = round(0.5 * max(w, h) * padding)
    # First pass on the bounding box.
    xmin = max(x0 - half_side, 0)
    ymin = max(y0 - half_side, 0)
    xmax = min(x0 + half_side, width - 1)
    ymax = min(y0 + half_side, height - 1)
    # Second pass to avoid exceeding the physical dimensions of the original image.
    w = xmax - xmin
    h = ymax - ymin
    if h > w:
        delta = (h - w) // 2
        ymin += delta
        ymax -= delta
    w = xmax - xmin
    h = ymax - ymin
    if abs(w - h) > 1:
        logger.warning('Skewed bounding box (width = %d, height = %d)', w, h)
    bbox = (xmin, ymin, xmax, ymax)
    logger.info('%d face candidate(s) found, last bbox = %s', len(faces), bbox)
    return bbox


EXIF_ORIENTATION_TAG = 274
EXIF_ROTATION_DICT = {3: 180, 6: 270, 8: 90}


def resize_presenter_pic(file_path: str, height: int, output_file_path: str = None, **kwargs):
    """Resize a given presented pic to the target height.
    """
    logger.info('Resizing %s...', file_path)
    kwargs.setdefault('resample', Image.ANTIALIAS)
    kwargs.setdefault('reducing_gap', 3.)
    try:
        with Image.open(file_path) as img:
            # Parse the original image size and orientation.
            w, h = img.size
            orientation = img.getexif().get(EXIF_ORIENTATION_TAG, None)
            logger.info('Original size: (%d, %d), orientation: %s', w, h, orientation)
            # If the image is rotated, we need to change the orientation.
            if orientation in EXIF_ROTATION_DICT:
                rotation = EXIF_ROTATION_DICT[orientation]
                logger.info('Applying a rotation by %d degrees...', rotation)
                img = img.rotate(rotation, expand=True)
                w, h = img.size
                logger.info('Rotated size: (%d, %d)', w, h)
            # Crop and scale to the target dimensions.
            bbox = face_bbox(file_path)
            logger.info('Resizing image to (%d, %d)...', height, height)
            img = img.resize((height, height), box=bbox, **kwargs)
            if output_file_path is not None:
                logger.info('Saving image to %s...', output_file_path)
                img.save(output_file_path)
    except PIL.UnidentifiedImageError as exception:
        logger.error(exception)
