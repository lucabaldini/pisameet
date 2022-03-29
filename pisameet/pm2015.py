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

import pdfrw

from __init__ import logger
from indico import retrieve_info, ConferenceInfo

BASE_NAME = 'pm2015'
LOCAL_ROOT = os.path.join('/data/work/', BASE_NAME)
INDICO_URL = 'https://agenda.infn.it/export/event/8397.json'
INFO_FILE_PATH = os.path.join(LOCAL_ROOT, f'{BASE_NAME}.json')
CONFIG_FILE_PATH = INFO_FILE_PATH.replace('.json', '.xlsx')
ATTACH_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'indico_attachments')
POSTER_FOLDER_PATH = os.path.join(LOCAL_ROOT, 'poster_original')

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

def pdf_info(file_path):
    """
    """
    try:
        pdf = pdfrw.PdfReader(file_path)
    except Exception as e:
        logger.error('Parsing error for %s: %s', file_path, e)
        return None, None
    num_pages = len(pdf.pages)
    box = pdf.pages[0].MediaBox
    if box is None:
        logger.error('No media box for %s...', file_path)
        return num_pages, None
    aspect_ratio = float(box[2]) / float(box[3])
    return num_pages, aspect_ratio

def poster_candidates(file_list):
    """
    """
    candidates = []
    for file_path in file_list:
        if file_path.endswith('.pdf'):
            num_pages, aspect_ratio = pdf_info(file_path)
            if num_pages == 1 and aspect_ratio is not None and aspect_ratio < 1:
                candidates.append(file_path)
    return candidates

def dispatch_files():
    """
    """
    ids = CONFERENCE_INFO.contribution_ids()
    file_dict = {id_: [] for id_ in ids}
    for file_name in os.listdir(ATTACH_FOLDER_PATH):
        if file_name.endswith('.tstamp'):
            continue
        id_ = int(file_name.split('-')[0])
        if id_ in file_dict:
            file_dict[id_].append(os.path.join(ATTACH_FOLDER_PATH, file_name))
    for id_, attachments in file_dict.items():
        if len(attachments) == 0:
            logger.error('No attachments found for contribution %d', id_)
            continue
        candidates = poster_candidates(attachments)
        if len(candidates) == 1:
            src = candidates[0]
            file_name = os.path.basename(src)
            dest = os.path.join(POSTER_FOLDER_PATH, file_name)
            logger.info('Copying over %s...', file_name)
            shutil.copyfile(src, dest)
        else:
            logger.warning('%d candidate posters / %d attachments for contribution %s',
                len(candidates), len(attachments), id_)



if __name__ == '__main__':
    #donwload_info()
    #download_attachments()
    #dump_config_file()
    dispatch_files()
