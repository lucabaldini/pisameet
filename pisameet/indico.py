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

"""INDICO interface.

This is using the INDICO API to help accessing the conference content, see
https://docs.getindico.io/en/stable/
"""

import datetime
import json

import pandas as pd
import requests

from __init__ import logger
from program import PosterRoster



def retrieve_info(url: str, file_path: str , detail: str = 'sessions'):
    """Retrieve the contributions, grouped by session for a given conference,
    following the instructions at
    https://docs.getindico.io/en/stable/http-api/exporters/event/#sessions

    According to the documentation, this setting details to "sessions" includes
    details about the different sessions and groups contributions by sessions.
    The top-level contributions list only contains contributions which are not
    assigned to any session. Subcontributions are included in this details level, too.

    Arguments
    ---------
    url : str
        The indico url for the conference, e.g., https://agenda.infn.it/export/event/8397.json

    file_path : str
        The path for the output .json file

    detail : str
        The level of detail for the dump, see
        https://docs.getindico.io/en/stable/http-api/exporters/event
    """
    assert file_path.endswith('.json')
    logger.info('Retrieving program from %s...', url)
    resp = requests.get(f'{url}?detail={detail}&pretty=yes')
    data = resp.json()
    logger.info('Saving data to %s...', file_path)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    logger.info('Done.')




class ConferenceInfo(dict):

    """Small convenience class describing the full list of contributions for a
    conference, see https://docs.getindico.io/en/stable/api/contribution/

    The underlying .json file is parsed as a Python dictionary containing the
    following keys at the top level:
    ['ts', 'url', 'additionalInfo', 'count', 'results', '_type']

    (If I understand correctly `count` is typically 1 and indicates the length
    of the `results` field, which is a list whose first element contains
    the actual data.)

    Now, `results[0]` is another dictionary whose keys are
    ['_type', 'id', 'title', 'description', 'startDate', 'timezone', 'endDate',
    'room', 'location', 'address', 'type', 'references', '_fossil', 'categoryId',
    'category', 'note', 'roomFullname', 'url', 'creationDate', 'creator',
    'hasAnyProtection', 'roomMapURL', 'folders', 'chairs', 'material', 'keywords',
    'visibility', 'contributions', 'sessions']

    The last two are the relevant pieces of information, containing the sessions,
    as well as the orphan contributions, if any.

    Each session is a dictionary with the following keys:
    ['_type', '_fossil', 'id', 'conference', 'startDate', 'endDate', 'description',
    'title', 'url', 'contributions', 'note', 'session', 'room', 'roomFullname',
    'location', 'inheritLoc', 'inheritRoom', 'slotTitle', 'address', 'conveners'],
    the most relevant fields being:

    * 'startDate', e.g., "{'date': '2015-05-28', 'time': '15:45:00', 'tz': 'Europe/Rome'}"
    * 'endDate', e.g., "{'date': '2015-05-28', 'time': '19:25:00', 'tz': 'Europe/Rome'}"
    * 'title', e.g., "Front end, Trigger, DAQ and Data Management"
    * 'url', e.g., "https://agenda.infn.it/event/8397/sessions/11528/"
    * 'contributions', listing all the contributions of the session.

    Finally, each entry in the list of contributions has the following keys:
    ['_type', '_fossil', 'id', 'db_id', 'friendly_id', 'title', 'startDate',
    'endDate', 'duration', 'roomFullname', 'room', 'note', 'location', 'type',
    'description', 'folders', 'url', 'material', 'speakers', 'primaryauthors',
    'coauthors', 'keywords', 'track', 'session', 'references', 'board_number']

    Arguments
    ---------
    file_path : str
        The path to the .json file containing all the contributions.
    """

    def __init__(self, file_path):
        """Constructor.
        """
        super().__init__()
        logger.info('Loading conference contributions from %s...', file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Parse the json hierarchy.
        results = data['results'][0]
        sessions = results['sessions']
        logger.info(f'{len(sessions)} session (s) found')
        contributions = results['contributions']
        if len(contributions):
            logger.warning(f'{len(contributions)} orphan contribution(s) found...')
        else:
            logger.info('No orphan contributions found...')
        # Populate the underlying dictionary.
        for session in sessions:
            self[session['title']] = session

    @staticmethod
    def attachment_urls(contribution):
        """
        """
        return [item['download_url'] for item in contribution['folders'][0]['attachments']]

    @staticmethod
    def pretty_print(contribution):
        """
        """
        identifier = contribution['friendly_id']
        try:
            speaker = contribution['speakers'][0]
            full_name = speaker['fullName']
        except IndexError:
            logger.warning('Cannot retrieve speaker for contribution %d', identifier)
            full_name = 'N/A'
        title = contribution['title']
        return f'[{identifier}] {full_name}: "{title}"'

    @staticmethod
    def _format_date(date_dict: str, fmt: str = PosterRoster.DATETIME_FORMAT):
        """Format a date in the .json file according to the date format in use
        for the excel configuration file.

        This means turning {'date': '2015-05-28', 'time': '15:45:00', 'tz': 'Europe/Rome'}
        into 28/05/2015 15:45.
        """
        text = f'{date_dict["date"]} {date_dict["time"]}'
        d = datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        return d.strftime(fmt)

    def dump_excel(self, file_path):
        """Dump the contribution list as an excel file.
        """
        logger.info(f'Dumping conference info to {file_path}...')
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

        # Create the master sheet with the session data.

        def _session_data(key):
            """Small nested function to facilitate the session data retrival.
            """
            if key in ('startDate', 'endDate'):
                return [self._format_date(session[key]) for session in self.values()]
            return [str(session[key]) for session in self.values()]

        data = [_session_data(key) for key in ('id', 'title', 'startDate', 'endDate')]
        df = pd.DataFrame({key: val for key, val in zip(PosterRoster.PROGRAM_COL_NAMES, data)})
        df.to_excel(writer, sheet_name=PosterRoster.PROGRAM_SHEET_NAME, index=False)
        sheet = writer.sheets[PosterRoster.PROGRAM_SHEET_NAME]
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 100)
        sheet.set_column(2, 3, 20)

        # Create the ancillary sheets with the actual contributions.

        def _contrib_data(session, key):
            """Small nested function to facilitate the session data retrival.
            """
            if key in ('first_name', 'last_name', 'affiliation'):
                try:
                    return [contrib['speakers'][0][key] for contrib in session['contributions']]
                except:
                    return 'N/A'
            return [contrib[key] for contrib in session['contributions']]

        for session in self.values():
            data = [_contrib_data(session, key) for key in ('id', 'title', 'first_name', 'last_name', 'affiliation')]
            data.insert(1, [''] * len(session['contributions']))
            df = pd.DataFrame({key: val for key, val in zip(PosterRoster.SESSION_COL_NAMES, data)})
            sheet_name = str(session['id'])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            sheet = writer.sheets[sheet_name]
            sheet.set_column(2, 2, 125)
            sheet.set_column(3, 4, 20)
            sheet.set_column(5, 5, 35)

        logger.info('Writing output file...')
        writer.save()
        logger.info('Done.')

    def __str__(self):
        """String formatting.
        """
        return '\n'.join([f'- {key} ({len(val["contributions"])} contributions)' \
            for key, val in self.items()])






if __name__ == '__main__':
    url = 'https://agenda.infn.it/export/event/8397.json'
    file_path = 'pm2015/pm2015.json'
    #retrieve_info(url, file_path)
    info = ConferenceInfo(file_path)
    print(info)
    info.dump_excel('pm2015/pm2015.xlsx')
