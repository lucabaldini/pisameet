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

from pisameet import logger
from pisameet.indico import retrieve_info, ConferenceInfo
from pisameet.dispatch import dispatch_posters

BASE_NAME = 'pm2022'
LOCAL_ROOT = os.path.join('/data/work/', BASE_NAME)
INDICO_URL = 'https://agenda.infn.it/export/event/22092.json'
INFO_FILE_PATH = os.path.join(LOCAL_ROOT, f'{BASE_NAME}.json')
CONFIG_FILE_PATH = INFO_FILE_PATH.replace('.json', '.xlsx')
ATTACH_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'indico_attachments')
POSTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'poster_original')

# Definition of the posted program---mind this has to be compiled by hand.
POSTER_PROGRAM = {
    26823: 'Photo Detectors and PID',
    26931: 'Cryogenic, Supeconductive and Quantum Devices',
    26826: 'Calorimetry',
    26822: 'Detector Systems and Future accelerators',
    26824: 'Solid State Detectors',
    26831: 'Front End, Trigger, DAQ and Data Mangement',
    26830: 'Gas Detectors'
    }

CONFERENCE_INFO = ConferenceInfo(INFO_FILE_PATH, POSTER_PROGRAM)


def donwload_info():
    """
    """
    retrieve_info(INDICO_URL, INFO_FILE_PATH)

def download_attachments():
    """
    """
    CONFERENCE_INFO.download_attachments(ATTACH_FOLDER_PATH)

def dump_config_file():
    """
    """
    CONFERENCE_INFO.dump_excel(CONFIG_FILE_PATH)

def dispatch_files():
    """
    """
    ids = CONFERENCE_INFO.contribution_ids()
    dispatch_posters(ids, ATTACH_FOLDER_PATH, POSTER_FOLDER_PATH)



if __name__ == '__main__':
    #donwload_info()
    #download_attachments()
    dump_config_file()
    #dispatch_files()
