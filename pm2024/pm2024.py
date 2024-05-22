# Copyright (C) 2022, luca.baldini@pi.infn.it
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

"""Sample file to exercise the system on the 2015 edition of the Pisa meeting.
"""

import os
import shutil
import sys

import pdfrw

from pisameet import logger, PISAMEET_BASE
from pisameet.indico import retrieve_info, ConferenceInfo
from pisameet.dispatch import dispatch_posters, dispatch_pictures
from pisameet.process import crawl
from pisameet.qrcode_ import generate_qrcode


# Basic conference info.
BASE_NAME = 'pm2024'
LOCAL_ROOT = os.path.join(PISAMEET_BASE, BASE_NAME)
INDICO_URL = 'https://agenda.infn.it/export/event/37033.json'
INFO_FILE_PATH = os.path.join(LOCAL_ROOT, f'{BASE_NAME}.json')
CONFIG_FILE_PATH = INFO_FILE_PATH.replace('.json', '.xlsx')

INDICO_ATTACHMENTS_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'indico_attachments')
POSTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'posters')
POSTER_RASTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'posters_raster')
PRESENTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'presenters')
PRESENTER_CROP_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'presenters_crop')
QRCODE_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'qrcodes')
SCREEN_TARGET_WIDTH = 1060
POSTER_TARGET_WIDTH = 2 * SCREEN_TARGET_WIDTH
POSTER_INTERMEDIATE_WIDTH = 2 * POSTER_TARGET_WIDTH


# Definition of the poster program---mind this has to be compiled by hand.
POSTER_PROGRAM = {
    36240: 'Photo Detectors and Particle ID',
    36242: 'Applications to Industrial and Societal Challenges',
    36239: 'Integration and Detector Systems',
    36241: 'Solid State Detectors',
    36243: 'Calorimetry',
    36245: 'Detector Techniques for Cosmology and Astroparticle Physics',
    36246: 'Gas Detectors',
    36247: 'Electronics and On-Detector Processing',
    36244: 'Low Temperature, Quantum and Emerging Technologies'
    }


def donwload_info(overwrite=False):
    """Download the json file with the conference program.
    """
    retrieve_info(INDICO_URL, INFO_FILE_PATH, overwrite=overwrite)


# If the json file does not exists, we create one on the fly.
if not os.path.exists(INFO_FILE_PATH):
    donwload_info()


CONFERENCE_INFO = ConferenceInfo(INFO_FILE_PATH, POSTER_PROGRAM)


def dump_config_file():
    """Parse the json file and dump and excel file with the conference program.
    """
    CONFERENCE_INFO.dump_excel(CONFIG_FILE_PATH)


def generate_qr_codes():
    """Generate all the relevant QR codes.
    """
    CONFERENCE_INFO.generate_qr_codes(QRCODE_FOLDER_PATH)
    for url, file_name in [
        ('https://agenda.infn.it/event/22092/timetable', 'timetable.png')
    ]:
        generate_qrcode(url, os.path.join(QRCODE_FOLDER_PATH, file_name))


def download_attachments(refresh_info=False):
    """Download all the attachments.

    This is downloading *all* the material for the relevant contributions for the
    specified contributions.
    """
    if refresh_info:
        donwload_info(overwrite=True)
    if not os.path.exists(INDICO_ATTACHMENTS_FOLDER_PATH):
        logger.info('Creating folder %s...' % INDICO_ATTACHMENTS_FOLDER_PATH)
        os.makedirs(INDICO_ATTACHMENTS_FOLDER_PATH)
    CONFERENCE_INFO.download_attachments(INDICO_ATTACHMENTS_FOLDER_PATH)


def dispatch_files():
    """Dispatch the files from the local download folder to the proper folder for
    later consumption by the slideshow and the program browser.
    """
    ids = CONFERENCE_INFO.contribution_ids()
    for folder_path in (POSTER_FOLDER_PATH, PRESENTER_FOLDER_PATH):
        if not os.path.exists(folder_path):
            logger.info('Creating folder %s...' % folder_path)
            os.makedirs(folder_path)
    dispatch_posters(ids, INDICO_ATTACHMENTS_FOLDER_PATH, POSTER_FOLDER_PATH)
    dispatch_pictures(ids, INDICO_ATTACHMENTS_FOLDER_PATH, PRESENTER_FOLDER_PATH)


def process_presenter_pic(file_path, height: int = 132, overwrite=False):
    """Process a single presenter pic.
    """
    file_name = os.path.basename(file_path)
    dest = os.path.join(PRESENTER_CROP_FOLDER_PATH, f'{file_name.split(".")[0]}.png')
    if os.path.exists(dest):
        logger.info('File %s already exists, skipping...', dest)
        return
    resize_presenter_pic(file_path, height, dest)

def process_presenter_pics(height: int = 132):
    """Process the presenter pics.
    """
    for file_name in os.listdir(PRESENTER_FOLDER_PATH):
        file_path = os.path.join(PRESENTER_FOLDER_PATH, file_name)
        process_presenter_pic(file_path)
