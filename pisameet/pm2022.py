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
from pisameet.dispatch import dispatch_posters


# Basic conference info.
BASE_NAME = 'pm2022'
LOCAL_ROOT = os.path.join(PISAMEET_BASE, BASE_NAME)
INDICO_URL = 'https://agenda.infn.it/export/event/22092.json'
INFO_FILE_PATH = os.path.join(LOCAL_ROOT, f'{BASE_NAME}.json')
CONFIG_FILE_PATH = INFO_FILE_PATH.replace('.json', '.xlsx')
ATTACH_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'indico_attachments')
POSTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'poster_original')
QRCODE_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'qrcodes')


# Definition of the posted program---mind this has to be compiled by hand.
POSTER_PROGRAM = {
    # Monday: S8P and S2P.
    26822: 'Detector Systems and Future accelerators',
    26961: 'Photo Detectors and PID',
    # Tuesday: S3P and S5P.
    26950: 'Solid State Detectors',
    26955: 'Application to life sciences and other societal challanges',
    # Wednesday: S4P.
    26956: 'Calorimetry',
    # Thursday: S9P and S1P.
    26957: 'Cryogenic, Supeconductive and Quantum Devices',
    26958: 'Detectors Techniques for Cosmology and Astroparticle Physics',
    # Friday: S6P and S7P.
    26959: 'Gas Detectors',
    26960: 'Front End, Trigger, DAQ and Data Mangement'
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


def download_attachments():
    """Download all the attachments.

    This is downloading *all* the material for the relevant contributions for the
    specified contributions.
    """
    CONFERENCE_INFO.download_attachments(ATTACH_FOLDER_PATH)


def dispatch_files():
    """Dispatch the files from the local download folder to the proper folder for
    later consumption by the slideshow and the program browser.
    """
    ids = CONFERENCE_INFO.contribution_ids()
    dispatch_posters(ids, ATTACH_FOLDER_PATH, POSTER_FOLDER_PATH)


def generate_qr_codes():
    """
    """
    CONFERENCE_INFO.generate_qr_codes(QRCODE_FOLDER_PATH)



if __name__ == '__main__':
    #dump_config_file()
    #download_attachments()
    #dispatch_files()
    generate_qr_codes()
