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

import glob
import os
import sys

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import QTimer


class SlideShow(QWidget):

    """Basic slideshow class.
    """

    # pylint: disable=too-many-instance-attributes
    DEFAULT_TIME_INTERVAL = 30.
    DEFAULT_PAUSE_TIME = 120.
    WINDOW_TITLE = '15th Pisa Meeting on Advanced Detectors'

    def __init__(self, folder_path, **kwargs):
        """Constructor.
        """
        super().__init__()
        # Parse the command-line arguments.
        time_interval = kwargs.get('time_interval', self.DEFAULT_TIME_INTERVAL)
        pause_time = kwargs.get('pause_time', self.DEFAULT_PAUSE_TIME)
        background_color = kwargs.get('background_color', 'black')
        geometry = kwargs.get('geometry')
        # Convert times from s to msec.
        self.time_interval = self.sec_to_msec(time_interval)
        self.pause_time = self.sec_to_msec(pause_time)
        # Reset the slideshow index.
        self.__current_index = 0
        # Setup the widget.
        self.setStyleSheet(f'background-color: {background_color}')
        self.label = QLabel()
        self._grid = QGridLayout()
        self._grid.setColumnStretch(0, 1)
        self._grid.setColumnStretch(2, 1)
        self._grid.addWidget(self.label, 1, 1)
        self.setLayout(self._grid)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance)
        # Load the images.
        self.pixmap_list, self.pixmap_keys = self._load_images(folder_path)
        self.show_image()
        # We're good to go!
        self.timer.start(self.time_interval)
        if geometry == 'maximized':
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

    def _load_images(self, folder_path: str, filters: tuple = ('png', 'jpg'), height: int = 1000):
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
        patterns = [os.path.join(folder_path, f'*.{ext}') for ext in filters]
        # Should you be tempted to use the builtin sum() with start=[], here,
        # keep in mind that can be used as a keyword argument only starting
        # from Python 3.8.
        file_list = []
        for pattern in patterns:
            file_list += glob.glob(pattern)
        # We want the file list sorted :-)
        file_list.sort()
        # Create the QPixmap objects.
        pixmap_list = []
        pixmap_keys = []
        for i, file_path in enumerate(file_list):
            print(f'Loading {file_path}...')
            pixmap_list.append(QPixmap(file_path).scaledToHeight(height))
            pixmap_keys.append(f'{i + 1}')
        self.__current_index = 0
        return pixmap_list, pixmap_keys

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Overloaded method to handle key events.
        """
        # pylint: disable=invalid-name
        if event.text() in self.pixmap_keys:
            index = int(event.text()) - 1
            self.show_image(index)
            self.timer.stop()
            self.timer.singleShot(self.pause_time, self.timer.start)

    def show_image(self, index: int = 0) -> None:
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
        self.label.setPixmap(self.pixmap_list[self.__current_index])

    def advance(self) -> None:
        """Advance to the next image.
        """
        self.show_image(self.__current_index + 1)



if __name__ == '__main__':
    # pylint: disable=invalid-name
    app = QApplication(sys.argv)
    slideshow = SlideShow('posters', time_interval=1.)
    sys.exit(app.exec_())
