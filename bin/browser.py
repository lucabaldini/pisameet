#!/usr/bin/env python3
#
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

"""Main slideshow application.
"""

import argparse
import os
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QTreeWidget, QTreeWidgetItem

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from pisameet.program import Poster, PosterSession
from pisameet import logger

PARSER = argparse.ArgumentParser()
PARSER.add_argument('cfgfile', type=str,
    help='path to the input excel configuration file')



class PosterProgram(dict):

    """
    """

    PROGRAM_SHEET_NAME = 'Program'
    DATETIME_FORMAT = '%d/%m/%Y %H:%M'
    PROGRAM_COL_NAMES = ('Session ID', 'Session Name', 'Start Date', 'End Date')
    SESSION_COL_NAMES = ('Poster ID', 'Screen ID', 'Title', 'First Name', 'Last Name', 'Affiliation')
    POSTER_FOLDER_NAME = 'poster_images'
    PRESENTER_FOLDER_NAME = 'presenters'
    QRCODE_FOLDER_NAME = 'qrcodes'

    def __init__(self, file_path : str) -> None:
        """Constructor
        """
        super().__init__()
        self.config_file_path = file_path
        self.root_folder_path = os.path.dirname(file_path)
        self.poster_folder_path = os.path.join(self.root_folder_path, self.POSTER_FOLDER_NAME)
        self.presenter_folder_path = os.path.join(self.root_folder_path, self.PRESENTER_FOLDER_NAME)
        self.qrcode_folder_path = os.path.join(self.root_folder_path, self.QRCODE_FOLDER_NAME)
        logger.info('Populating program...')
        logger.debug('Reading %s sheet from %s...', self.PROGRAM_SHEET_NAME, self.config_file_path)
        program_df = pd.read_excel(self.config_file_path, self.PROGRAM_SHEET_NAME)
        for _, program_row in program_df.iterrows():
            session = PosterSession.from_df_row(program_row)
            self[session] = []
            try:
                session_df = pd.read_excel(self.config_file_path, str(session.name))
                for _, session_row in session_df.iterrows():
                    poster = Poster.from_df_row(session_row)
                    print(poster)
                    self[session].append(poster)
            except Exception as e:
                logger.warning('Data not available for session %s: %s', session.name, e)



class ProgramTreeWidget(QTreeWidget):

    """
    """

    def __init__(self, width):
        """
        """
        super().__init__()
        self.setColumnCount(3)
        self.setHeaderLabels(['Session/Poster', 'Presenter', 'Affiliation'])
        self.setColumnWidth(0, int(0.6 * width))
        self.setColumnWidth(1, int(0.2 * width))
        self.header().setStretchLastSection(True)



class Browser(QWidget):

    """
    """

    WINDOW_TITLE = '15th Pisa Meeting on Advanced Detectors -- Poster Browser'

    def __init__(self, **kwargs):
        """Constructor.
        """
        super().__init__()
        self.setStyleSheet('background-color: "white"')
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setLayout(QGridLayout())

        poster_width = kwargs.get('poster_width')
        self.layout().setColumnMinimumWidth(0, poster_width)
        self.tree_widget = ProgramTreeWidget(poster_width)
        self.layout().addWidget(self.tree_widget, 0, 0)
        self.tree_widget.itemPressed.connect(self.display_poster)
        self.program = PosterProgram(kwargs.get('cfgfile'))
        items = []
        for session, posters in self.program.items():
            item = QTreeWidgetItem([session.title])
            for poster in posters:
                presenter = poster.presenter
                affiliation = presenter.affiliation
                if pd.isna(affiliation):
                    affiliation = 'N/A'
                values = [poster.title, presenter.full_name(), affiliation]
                child = QTreeWidgetItem(values)
                item.addChild(child)
            items.append(item)
        self.tree_widget.insertTopLevelItems(0, items)
        self.showMaximized()

    def keyPressEvent(self, event):
        """
        """
        print(event)
        print(self.tree_widget.currentItem().data(0, 0))

    def display_poster(self, *args):
        """
        """
        print('Display poster!')
        print(args)



if __name__ == '__main__':
    args = PARSER.parse_args()
    app = QApplication(sys.argv)
    kwargs = args.__dict__
    # Determine the appropriate poster width from the screen size unless this is
    # explicitly overridden via command-line options.
    if kwargs.get('poster_width') is None:
        poster_width = app.screens()[0].size().width() - 20
        logger.info('Setting posted width to %d (based on the screen size)', poster_width)
        kwargs['poster_width'] = poster_width
    browser = Browser(**kwargs)
    sys.exit(app.exec_())
