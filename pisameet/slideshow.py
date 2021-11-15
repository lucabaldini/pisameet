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
import glob
import logging
import os
import sys

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt, QTimer

import touchphat


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



class Pixmap(QPixmap):

    """Lightweight wrapper around a QPixmap object.

    This is building on the standard QPixmap class to make a timestamp-aware
    object able to reload the image data whenever the underlying file is changed
    on disk. In addition, we keep track of the pixmap height and the keyboard
    shortcut associated to the image.

    Arguments
    ---------
    file_path : str
        The path to the image file.

    key : str
        The associated key to be used to pause the slideshow from the keyboard.

    height : int
        The target height for the image resize.
    """

    def __init__(self, file_path: str, key: str, height: int) -> None:
        """Constructor.
        """
        super().__init__()
        self.file_path = file_path
        self.key = key
        self.height = height
        self.timestamp = self._read_timestamp()
        self._load_data()

    def _read_timestamp(self) -> float:
        """Return the last modification timestamp for the underlying file.

        See https://stackoverflow.com/questions/237079 for more details about
        retrieving the last modification timestamp for a file.
        """
        return os.path.getmtime(self.file_path)

    def _load_data(self) -> None:
        """Load the image data from file and resize the pixmap to the target height.

        Note that it is *very* important to call the QPixmap.scaledToHeight()
        method with the Qt.SmoothTransformation transformation mode, so that
        a bilinear interpolation is performed when remapping the original
        image into the target QLabel object.
        """
        logger.debug('Loading image data from %s...', self.file_path)
        QPixmap.load(self, self.file_path)
        logger.debug('Resizing image...')
        super().__init__(self.scaledToHeight(self.height, Qt.SmoothTransformation))

    def synch(self) -> None:
        """Check whether the underlying file has been modified, and reload the
        image data if necessary.
        """
        _ts = self._read_timestamp()
        if _ts > self.timestamp:
            logger.warning('File %s has been modified on disk, reloading data...', self.file_path)
            self._load_data()
            self.timestamp = _ts



class PixmapList(list):

    """Class describing a list of pixmaps.

    The constructor is crawling through a given folder and loading in memeory
    all the image files for later use.
    """

    def __init__(self, folder_path: str, screen_id: int, height: int) -> None:
        """Constructor.
        """
        super().__init__()
        self._key_dict = {}
        for i, file_path in enumerate(self.build_file_list(folder_path, screen_id)):
            key = self.pixmap_key(i)
            self.append(Pixmap(file_path, key, height))
            self._key_dict[key] = i

    @staticmethod
    def pixmap_key(index: int) -> str:
        """Return the key corresponding to a given sequential index.
        """
        return f'{index + 1}'

    def pixmap_index(self, key: str) -> int:
        """Return the index corresponding to a given key, if valid.
        """
        return self._key_dict.get(key, None)

    def file_list(self):
        """Return the underlying (cached) file list.
        """
        return [pixmap.file_path for pixmap in self]

    @staticmethod
    def build_file_list(folder_path: str, screen_id: int, filters: tuple = ('png', 'jpg')) -> None:
        """Process a folder content and build the list of image files.
        """
        _start = f'{screen_id:02d}_'
        file_list = []
        logger.info('Compiling file list from %s...', folder_path)
        for file_path in glob.glob(os.path.join(folder_path, '*.*')):
            if file_path.split('.').pop() not in filters:
                continue
            if not os.path.basename(file_path).startswith(_start):
                continue
            file_list.append(file_path)
        file_list.sort()
        logger.info('Done, %d image file(s) found.', len(file_list))
        return file_list



class SlideShow(QWidget):

    """Basic slideshow class.
    """

    DEFAULT_ADVANCE_INTERVAL = 30.
    DEFAULT_PAUSE_INTERVAL = 120.
    WINDOW_TITLE = '15th Pisa Meeting on Advanced Detectors'
    VALID_GEOMETRIES = ('default', 'maximize', 'fullscreen')

    def __init__(self, folder_path: str, screen: int, **kwargs):
        """Constructor.
        """
        super().__init__()
        self.folder_path = folder_path
        self.screen_id = screen
        # Parse the command-line arguments.
        advance_interval = kwargs.get('advance', self.DEFAULT_ADVANCE_INTERVAL)
        pause_interval = kwargs.get('pause', self.DEFAULT_PAUSE_INTERVAL)
        background_color = kwargs.get('background', 'black')
        geometry = kwargs.get('geometry')
        self.height = kwargs.get('height')
        assert geometry in self.VALID_GEOMETRIES
        # Convert times from s to msec.
        self.advance_interval = self.sec_to_msec(advance_interval)
        self.pause_interval = self.sec_to_msec(pause_interval)
        # Reset the slideshow index.
        self.__current_index = 0
        self.pixmap_list = []
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
        self._load_images()
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

    def _load_images(self):
        """Load all the images from the target folder.

        This is reading the files from disk, creating the corresponding
        QPixmap objects and resizing them to the proper size, so that they are
        ready to be displyed in the main QLabel object. Note we also set the
        __current_index class member to 0.

        .. warning::

            Ideally we would infer the height parameter from the main window,
            after it has been displayed in full-screen or presentation mode,
            but I didn't find a sensible way to gauge the geometry under X11.

        Arguments
        ---------
        height : int
            The target height (in pixel) for the QPixmap(s) showing the images.
        """
        self.__current_index = 0
        self.pixmap_list = PixmapList(self.folder_path, self.screen_id, self.height)
        if len(self.pixmap_list) == 0:
            logger.error('No suitable image file(s) found.')
            sys.exit('Abort.')

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Overloaded method to handle key events.
        """
        # pylint: disable=invalid-name
        print(event.text())
        index = self.pixmap_list.pixmap_index(event.text())
        if index is None:
            return
        self.display_image(index)
        self.timer.stop()
        self.timer.singleShot(self.pause_interval, self.timer.start)

    @touchphat.on_touch(['Back', 'A', 'B', 'C', 'D', 'Enter'])
    def handle_touch(event):
        """
        """
        print(event.name)

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
        current_file_list = PixmapList.build_file_list(self.folder_path, self.screen_id)
        cached_file_list = self.pixmap_list.file_list()
        if cached_file_list != current_file_list:
            logger.warning('Poster folder changed on disk!')
            self._load_images()
        else:
            self.__current_index = index % len(self.pixmap_list)
        logger.debug('Displaying image %s...', PixmapList.pixmap_key(self.__current_index))
        pixmap = self.pixmap_list[self.__current_index]
        pixmap.synch()
        self.label.setPixmap(pixmap)

    def advance(self) -> None:
        """Advance to the next image.
        """
        self.display_image(self.__current_index + 1)



if __name__ == '__main__':
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser()
    parser.add_argument('--screen', type=int, default=1,
                        help='the unique identifier of the target screen')
    parser.add_argument('--advance', type=float, default=SlideShow.DEFAULT_ADVANCE_INTERVAL,
                        help='the time interval for the slide show transition [s]')
    parser.add_argument('--pause', type=float, default=SlideShow.DEFAULT_PAUSE_INTERVAL,
                        help='the time interval for the slide show pause [s]')
    parser.add_argument('--geometry', type=str, default='default', choices=SlideShow.VALID_GEOMETRIES,
	                help='display geometry')
    parser.add_argument('--height', type=int, default=1000,
                        help='the target image height')
    parser.add_argument('--background', type=str, default='black',
                        help='the widget background color')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    slideshow = SlideShow('posters', **args.__dict__)
    sys.exit(app.exec_())
