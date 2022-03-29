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

from indico import retrieve_info, ConferenceInfo

BASE_NAME = 'pm2015'
LOCAL_ROOT = os.path.join('/data/work/', BASE_NAME)
INDICO_URL = 'https://agenda.infn.it/export/event/8397.json'
INFO_FILE_PATH = os.path.join(LOCAL_ROOT, f'{BASE_NAME}.json')
CONFIG_FILE_PATH = INFO_FILE_PATH.replace('.json', '.xlsx')
ATTACH_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'indico_attachments')

# Definition of the posted program---mind this has to be compiled by hand.
POSTER_PROGRAM = {
    13095: 'Applications',
    13091: 'Photo Detectors and PID',
    13099: 'Gas Detectors',
    13097: 'Applied Superconductivity in HEP',
    13103: 'Front end, Trigger, DAQ and Data Management',
    13101: 'Solid State Detectors',
    13107: 'Calorimetry',
    13105: 'Detector Techniques for Cosmology, Astroparticle and General Physics',
    13089: 'Run2 at LHC'
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



if __name__ == '__main__':
    donwload_info()
    download_attachments()
    dump_config_file()
