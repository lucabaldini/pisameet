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

import json
import requests

from __init__ import logger



def retrieve_contributions(url, file_path):
    """Retrieve the contributions for a given conference, following the
    instructions at
    https://docs.getindico.io/en/stable/http-api/exporters/event/#contributions
    """
    assert file_path.endswith('.json')
    logger.info('Retrieving program from %s...', url)
    resp = requests.get(f'{url}?detail=contributions&pretty=yes')
    data = resp.json()
    logger.info('Saving data to %s...', file_path)
    with open(file_path, 'w') as f:
        json.dump(data, f)
    logger.info('Done.')




class ContributionList(list):

    """Small convenience class describing the full list of contributions for a
    conference, see https://docs.getindico.io/en/stable/api/contribution/

    Each entry in the list is a small dictionary with the following keys:
    '_type', '_fossil', 'id', 'db_id', 'friendly_id', 'title', 'startDate',
    'endDate', 'duration', 'roomFullname', 'room', 'note', 'location', 'type',
    'description', 'folders', 'url', 'material', 'speakers', 'primaryauthors',
    'coauthors', 'keywords', 'track', 'session', 'references', 'board_number'

    Arguments
    ---------
    file_path : str
        The path to the .json file containing all the contributions.
    """

    def __init__(self, file_path=None):
        """Constructor.
        """
        if file_path is not None:
            logger.info('Loading conference contributions from %s...', file_path)
            with open(file_path, 'r') as f:
                data = json.load(f)
            super().__init__(data['results'][0]['contributions'])
            logger.info('Done, %d contribution(s) found.', len(self))
        else:
            super().__init__()

    @staticmethod
    def attachment_urls(entry):
        """
        """
        return [item['download_url'] for item in entry['folders'][0]['attachments']]

    @staticmethod
    def pretty_print(entry):
        """
        """
        identifier = entry['friendly_id']
        try:
            speaker = entry['speakers'][0]
            full_name = speaker['fullName']
        except IndexError:
            logger.warning('Cannot retrieve speaker for contribution %d', identifier)
            full_name = 'N/A'
        title = entry['title']
        return f'[{identifier}] {full_name}: "{title}"'

    def filter(self, **kwargs):
        """Filter the contribution list based on some criteria.
        """
        sel = self.__class__()
        for entry in self:
            for key, value in kwargs.items():
                if entry[key] != value:
                    continue
                sel.append(entry)
        return sel

    def __str__(self):
        """String formatting.
        """
        return '\n'.join([self.pretty_print(entry) for entry in self])





if __name__ == '__main__':
    url = 'https://agenda.infn.it/export/event/8397.json'
    file_path = 'pm2015/pm2015.json'
    #retrieve_contributions(url, file_path)
    cl = ContributionList(file_path)
    print(cl)
    #cl = cl.filter(session='Detector Techniques for Cosmology, Astroparticle and Fundamental Physics - Poster Session')
