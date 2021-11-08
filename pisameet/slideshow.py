#!/usr/bin/env python3
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

"""Tools for the poster slideshow.
"""

import argparse
import datetime
import logging
import os
import sys

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import QTimer



class TerminalColors:

    """Terminal facilities for printing text in colors.
    """

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def _color(text, color):
        """Process a piece of tect to be printed out in color.
        """
        return '%s%s%s' % (color, text, TerminalColors.ENDC)

    @staticmethod
    def red(text):
        """Process a piece of text to be printed out in red.
        """
        return TerminalColors._color(text, TerminalColors.RED)

    @staticmethod
    def yellow(text):
        """Process a piece of text to be printed out in yellow.
        """
        return TerminalColors._color(text, TerminalColors.YELLOW)

    @staticmethod
    def green(text):
        """Process a piece of text to be printed out in green.
        """
        return TerminalColors._color(text, TerminalColors.GREEN)



class TerminalFormatter(logging.Formatter):

    """Logging terminal formatter class.
    """

    def format(self, record):
        """Overloaded format method.
        """
        text = ('>>> %s' % record.msg)
        if len(record.args) > 0:
            text = text % record.args
        if record.levelno >= logging.ERROR:
            text = TerminalColors.red(text)
        elif record.levelno == logging.WARNING:
            text = TerminalColors.yellow(text)
        return text


#Configure the main terminal logger.
logger = logging.getLogger('pisameet')
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(TerminalFormatter())
logger.addHandler(consoleHandler)



class FolderDescriptor:

    """Small container class to keep track of the image files to be looped
    over in a given directory.
    """

    DEFAULT_FILTERS = ('png', 'jpg')

    def __init__(self, folder_path: str, filters: tuple = DEFAULT_FILTERS) -> None:
        """Constructor.
        """
        self.file_list = []
        logger.info('Scanning input folder %s...', folder_path)
        for entry in os.scandir(folder_path):
            if not entry.is_file():
                continue
            file_path = entry.path
            if file_path.split('.').pop() not in filters:
                continue
            stat = entry.stat()
            mod_timestamp = stat.st_mtime
            self.file_list.append((file_path, mod_timestamp))
        self.file_list.sort()
        logger.info('Done, %d image file(s) found.\n%s', len(self.file_list), self)

    def pixmap_data(self, height: int):
        """Load the image data and create the relevant QPixmap objects.
        """
        logger.info('Loading pixmap data...')
        pixmap_list = []
        pixmap_keys = []
        for i, (file_path, _) in enumerate(self.file_list):
            logger.info('Loading image from %s...', file_path)
            pixmap_list.append(QPixmap(file_path).scaledToHeight(height))
            pixmap_keys.append(f'{i + 1}')
        return pixmap_list, pixmap_keys

    def __str__(self) -> str:
        """String formatting.
        """
        text = ''
        for i, (file_path, mod_timestamp) in enumerate(self.file_list):
            mode_date = datetime.datetime.fromtimestamp(mod_timestamp)
            text = f'{text}[{i}] {file_path} -> {mode_date}\n'
        return text.strip('\n')



class SlideShow(QWidget):

    """Basic slideshow class.
    """

    DEFAULT_ADVANCE_INTERVAL = 30.
    DEFAULT_PAUSE_INTERVAL = 120.
    WINDOW_TITLE = '15th Pisa Meeting on Advanced Detectors'
    VALID_GEOMETRIES = ('default', 'maximize', 'fullscreen')

    def __init__(self, folder_path, **kwargs):
        """Constructor.
        """
        super().__init__()
        # Parse the command-line arguments.
        advance_interval = kwargs.get('advance', self.DEFAULT_ADVANCE_INTERVAL)
        pause_interval = kwargs.get('pause', self.DEFAULT_PAUSE_INTERVAL)
        background_color = kwargs.get('background', 'black')
        geometry = kwargs.get('geometry')
        assert geometry in self.VALID_GEOMETRIES
        # Convert times from s to msec.
        self.advance_interval = self.sec_to_msec(advance_interval)
        self.pause_interval = self.sec_to_msec(pause_interval)
        # Reset the slideshow index.
        self.__current_index = 0
        # Setup the widget.
        self.setStyleSheet(f'background-color: {background_color}')
        self.label = QLabel()
        _grid = QGridLayout()
        _grid.setColumnStretch(0, 1)
        _grid.setColumnStretch(2, 1)
        _grid.addWidget(self.label, 1, 1)
        self.setLayout(_grid)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance)
        # Load the images.
        self.pixmap_list, self.pixmap_keys = self._load_images(folder_path)
        self.display_image()
        # We're good to go!
        self.timer.start(self.advance_interval)
        if geometry == 'maximize':
            self.showMaximized()
        elif geometry == 'fullscreen':
            self.showFullScreen()
        else:
            self.show()

    @staticmethod
    def sec_to_msec(sec: float) -> int:
        """Convert a time from seconds to ms.

        Arguments
        ---------
        sec : float
            The time interval in s.

        Return
        ------
            The time interval in ms, rounded to the nearest integer.
        """
        return int(round(1.e3 * sec))

    def _load_images(self, folder_path: str, height: int = 1000):
        """Load all the images from the target folder.

        This is reading the files from disk, creating the corresponding
        QPixmap objects and resizing them to the proper size, so that they are
        ready to be displyed in the main QLabel object. The main idea is that
        all the I/O and computations happen once, at the beginning, and then
        we just set the proper QPixmap to the main QLabel.

        Also, this is filling the list of characters to be associated to each
        image, that can be used later to process QKeyEvents.

        Note we set the __current_index class member to 0.

        .. warning::

            Ideally we would infer the height parameter from the main window,
            after it has been displayed in full-screen or presentation mode,
            but I didn't find a sensible way to gauge the geometry under X11.

        Arguments
        ---------
        folder_path : str
            The path to the folder containing the poster images.

        filter : tuple or list of strings
            A tuple or list containing all the file extensions to search for in
            the folder passed as a first argument.

        height : int
            The target height (in pixel) for the QPixmap(s) showing the images.

        Return
        ------
        Two lists of the same length, containing the QPixmap objects and the
        characters for the key shortcuts.
        """
        self.__current_index = 0
        return FolderDescriptor(folder_path).pixmap_data(height)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Overloaded method to handle key events.
        """
        # pylint: disable=invalid-name
        if event.text() in self.pixmap_keys:
            index = int(event.text()) - 1
            self.show_image(index)
            self.timer.stop()
            self.timer.singleShot(self.pause_interval, self.timer.start)

    def display_image(self, index: int = 0) -> None:
        """Show a given image.

        This is setting the proper QPixmap object to be shown and setting the
        __current_index class member.

        Arguments
        ---------
        index : int
            The index of the image to be shown (note this is intended modulo the
            total number of images in the slideshow).
        """
        self.__current_index = index % len(self.pixmap_list)
        logger.debug('Displaying image %d...', self.__current_index)
        self.label.setPixmap(self.pixmap_list[self.__current_index])

    def advance(self) -> None:
        """Advance to the next image.
        """
        self.display_image(self.__current_index + 1)



if __name__ == '__main__':
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser()
    parser.add_argument('--advance', type=float, default=SlideShow.DEFAULT_ADVANCE_INTERVAL,
        help='the time interval for the slide show transition [s]')
    parser.add_argument('--pause', type=float, default=SlideShow.DEFAULT_PAUSE_INTERVAL,
        help='the time interval for the slide show pause [s]')
    parser.add_argument('--geometry', type=str, default='default', choices=SlideShow.VALID_GEOMETRIES,
        help='the widget geometry')
    parser.add_argument('--background', type=str, default='black',
        help='the widget background color')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    slideshow = SlideShow('posters', **args.__dict__)
    sys.exit(app.exec_())
