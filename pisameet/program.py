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

"""Basic description of the conference program.
"""

import datetime
import os
import pathlib

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from __init__ import logger



class Presenter:

    """Presenter descriptor.

    Arguments
    ---------
    first_name : str
        The presenter first name (including middle name initials where appropriate).

    last_name : str
        The presenter last name.

    affiliation : str
        The presenter affiliation.
    """

    def __init__(self, first_name : str, last_name : str, affiliation: str) -> None:
        """Constructor
        """
        self.first_name = first_name
        self.last_name = last_name
        self.affiliation = affiliation

    def full_name(self) -> str:
        """Return the presenter full name.
        """
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        """String formatting.
        """
        return f'{self.full_name()} ({self.affiliation})'



class Poster:

    """Poster descriptor.

    Arguments
    ---------
    unique_id : int
        The unique identifier assigned to the poster.

    screen_id :  int
        The identifier of the screen the poster needs to be projected on.

    title : str
        The poster title.

    presenter : Presenter instance
        The poster presenter.
    """

    def __init__(self, unique_id : int, screen_id : int, title : str, presenter) -> None:
        """Constructor.
        """
        self.unique_id = unique_id
        self.screen_id = screen_id
        self.title = title
        self.presenter = presenter
        self.poster_pixmap = None
        self.presenter_pixmap = None
        self.qrcode_pixmap = None

    @classmethod
    def from_df_row(cls, row):
        """Create a PosterSession object from a dataframe row.
        """
        args = [row[col_name] for col_name in PosterRoster.SESSION_COL_NAMES]
        return cls(*args[:-3], Presenter(*args[-3:]))

    def short_title(self, max_chars=40):
        """Return a shortened version of the title, trimmed to a fixed maximum
        number of characters if too long.
        """
        if len(self.title) <= max_chars:
            return self.title.ljust(max_chars)
        else:
            return f'{self.title[:max_chars - 3]}...'

    def load_pixmap(self, file_path : str, height : int, width : int=None):
        """
        """
        logger.debug('Loading image data from %s...', file_path)
        return QPixmap(file_path).scaledToHeight(height, Qt.SmoothTransformation)

    def load_data(self, poster_file_path, pic_file_path, qrcode_file_path,
        poster_size, header_height):
        """Load all the necessary poster data.
        """
        logger.info('Loading data for poster %s...', self)
        if poster_file_path is None:
            logger.error('Poster file path undefined for %s', self)
        else:
            width, height = poster_size
            self.poster_pixmap = self.load_pixmap(poster_file_path, height)
        if pic_file_path is None:
            logger.warning('Pic file path undefined for %s', self)
        else:
            self.presenter_pixmap = self.load_pixmap(pic_file_path, header_height)

    def __str__(self):
        """String formatting.
        """
        return f'[{self.unique_id:03}] {self.short_title()} ({self.presenter.full_name()})'



class PosterSession:

    """Poster session descriptor.
    """

    def __init__(self, name, title, start, end):
        """Constructor
        """
        self.name = name
        self.title = title
        self.start = self.parse_datetime(start)
        self.end = self.parse_datetime(end)

    def parse_datetime(self, text):
        """Parse a datetime string in the proper format.
        """
        try:
            return datetime.datetime.strptime(text, PosterRoster.DATETIME_FORMAT)
        except Exception as e:
            logger.warning('Invalid date and/or time for session %s (%s).', self.name, e)
            return None

    @classmethod
    def from_df_row(cls, row):
        """Create a PosterSession object from a dataframe row.
        """
        return cls(*[row[col_name] for col_name in PosterRoster.PROGRAM_COL_NAMES])

    def ongoing(self) -> bool:
        """Return True if the session is ongoing.
        """
        return self.start is not None and self.end is not None and \
            self.start <= datetime.datetime.now() <= self.end

    def __str__(self):
        """String formatting.
        """
        return f'Session {self.name} ({self.title})'



class PosterRoster(list):

    """Poster roster description.

    Arguments
    ---------
    config_file_path : str
        The path to the excel config file with the poster program.

    root_folder_path : str
        The path to the root folder containing the session material.

    screen_id : int
        The screen identifier for the poster roster.

    Note this is streamlined for speed, as we don't have very many resources
    on the raspberry PI.
    """

    PROGRAM_SHEET_NAME = 'Program'
    DATETIME_FORMAT = '%d/%m/%Y %H:%M'
    PROGRAM_COL_NAMES = ('Session ID', 'Session Name', 'Start Date', 'End Date')
    SESSION_COL_NAMES = ('Poster ID', 'Screen ID', 'Title', 'First Name', 'Last Name', 'Affiliation')
    POSTER_FOLDER_NAME = 'poster_imgs'
    PIC_FOLDER_NAME = 'pics'

    def __init__(self, config_file_path : str, root_folder_path : str, screen_id : int) -> None:
        """Constructor
        """
        super().__init__()
        self.config_file_path = config_file_path
        self.root_folder_path = root_folder_path
        self.poster_folder_path = os.path.join(self.root_folder_path, self.POSTER_FOLDER_NAME)
        self.pic_folder_path = os.path.join(self.root_folder_path, self.PIC_FOLDER_NAME)
        self.screen_id = screen_id
        logger.info('Populating session list...')
        logger.debug('Reading %s sheet from %s...', self.PROGRAM_SHEET_NAME, config_file_path)
        program_df = pd.read_excel(config_file_path, self.PROGRAM_SHEET_NAME)
        for _, program_row in program_df.iterrows():
            session = PosterSession.from_df_row(program_row)
            if not session.ongoing():
                continue
            logger.info('Parsing ongoing %s...', session)
            try:
                session_df = pd.read_excel(config_file_path, session.name)
                for _, session_row in session_df.iterrows():
                    poster = Poster.from_df_row(session_row)
                    if poster.screen_id == self.screen_id:
                        self.append(poster)
            except ValueError as e:
                logger.warning('Data not available for session %s: %s', session.name, e)
            self.session = session
            break

    @staticmethod
    def _poster_id(file_path, separator='-'):
        """Extract the poster identifier from the file path.

        It is assumed that the file path starts with the poster identifier, followed
        by the separator---and then the rest of the path.

        Arguments
        ---------
        file_path : pathlib.Path object
            The file path

        separator : str
            The separator to match the initial poster identifier.
        """
        try:
            return int(file_path.name.split(separator)[0])
        except ValueError as e:
            logger.error('Invalid file name %s (%s)', file_path, e)
            return None

    def _file_dict(self, folder_path, poster_ids, *extensions):
        """Retrieve all the files in a given folder matching a given list of
        poster identifiers (and with the proper file extension).
        """
        logger.info('Scanning folder %s for files...', folder_path)
        file_dict = {}
        for file_path in pathlib.Path(folder_path).iterdir():
            if file_path.suffix in extensions:
                poster_id = self._poster_id(file_path)
                if poster_id in poster_ids:
                    file_dict[poster_id] = str(file_path)
        num_files = len(file_dict)
        num_posters = len(poster_ids)
        if num_files != num_posters:
            logger.warning('Only %d file(s) out of %d were found.', num_files, num_posters)
            for poster_id in poster_ids:
                if poster_id not in file_dict:
                    logger.warning('Poster %d is orphan.', poster_id)
        logger.info('Done')
        for key, value in file_dict.items():
            logger.debug('[%03d] %s', key, value)
        return file_dict

    def load_poster_data(self, poster_size, header_height):
        """Load all the poster data.

        Note that much of the logic, here, could be deferred to the Poster class
        in a way that would probably look neater, but that would also imply
        multiple listings of the same folder, which we'd rather avoid.
        """
        logger.info('Loading poster data...')
        poster_ids = [poster.unique_id for poster in self]
        poster_file_dict = self._file_dict(self.poster_folder_path, poster_ids, '.png')
        pic_file_dict = self._file_dict(self.pic_folder_path, poster_ids, '.png', '.jpg', '.jpeg')
        qrcode_file_dict = {}
        for poster in self:
            args = [d.get(poster.unique_id) for d in (poster_file_dict, pic_file_dict, qrcode_file_dict)]
            args += [poster_size, header_height]
            poster.load_data(*args)

    def __str__(self):
        """String formatting.
        """
        return f'Roster for screen {self.screen_id}\n' + '\n'.join([str(poster) for poster in self])



if __name__ == '__main__':
    config_file_path = '/data/work/pisameet/pisameet/config/pm2018_sample.xlsx'
    root_folder_path = '/data/work/pm18/'
    screen_id = 1
    roster = PosterRoster(config_file_path, root_folder_path, screen_id)
    print(roster)
