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

"""Graphical user interface.
"""


import argparse
import os
import sys

# pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt, QTimer

from __init__ import logger, read_screen_id
from program import PosterRoster



class FadingEffect(QGraphicsOpacityEffect):

    """Graphic effect for picture fade-in/out.

    This is simple graphic effect allowing a fade-in/out effect to a gradual
    change in the opacity. Internally, the transitions are controlled via a
    QTimer() object increasing or decreasing the opacity by a fixed amount
    (the _step class member) at each timeout.

    Arguments
    ---------
    step : float
        The basic opacity step used when increasing/decreasing the opacity.

    interval : int
        The basic time interval (in ms) during the transitions.
    """

    def __init__(self, step: float = 0.025, interval: int = 5):
        """Constructor.
        """
        super().__init__()
        self.setOpacity(1.)
        self._step = step
        self._interval = interval
        self._timer = QTimer()
        self._timer.start(self._interval)
        logger.debug('Opacity fade time set to %.3f s', self.fade_time())

    def fade_time(self):
        """Return the total fade-in/out time in seconds, i.e., the time that it
        takes for the opacity to change all the way from 0 to 1 or vice-versa.
        """
        return 1.e-3 * self._interval / self._step

    def _decrease_opacity(self):
        """Decrease the opacity by one step.

        Since this is typically controlled by the underlying QTimer object, when
        the opacity reaches (or crosses) zero the timer is disconnected from all
        the slots, and the opacity is set to 0 (fully opaque).
        """
        opacity = self.opacity() - self._step
        if opacity <= 0.:
            self._timer.disconnect()
            self.setOpacity(0.)
        self.setOpacity(opacity)

    def _increase_opacity(self):
        """Increase the opacity by one step.

        Since this is typically controlled by the underlying QTimer object, when
        the opacity reaches (or crosses) one the timer is disconnected from all
        the slots, and the opacity is set to 1 (fully transparent).
        """
        opacity = self.opacity() + self._step
        if opacity >= 1.:
            self._timer.disconnect()
            self.setOpacity(1.)
        self.setOpacity(opacity)

    def fade_in(self, start_from_zero=True):
        """Fade in effect, i.e., gradually change opacity to 1.
        """
        if start_from_zero:
            self.setOpacity(0.)
        self._timer.timeout.connect(self._increase_opacity)

    def fade_out(self, start_from_one=True):
        """Fade in effect, i.e., gradually change opacity to 0.
        """
        if start_from_one:
            self.setOpacity(1.)
        self._timer.timeout.connect(self._decrease_opacity)



class WidgetBase(QWidget):

    """Base class for the slideshow widgets.

    This is basically a QWidget with a built-in QGridLayout.
    """

    def __init__(self, column_stretch: dict={}, **kwargs):
        """Constructor.
        """
        super().__init__()
        grid = QGridLayout()
        for col, stretch in column_stretch.items():
            grid.setColumnStretch(col, stretch)
        self.setLayout(grid)
        background_color = kwargs.get('background')
        if background_color is not None:
            self.setStyleSheet(f'background-color: {background_color}')

    def add_widget(self, widget, row, col, row_span=1, col_span=1, alignment=Qt.AlignHCenter):
        """Add a widget to the underlying grid layout.
        """
        self.layout().addWidget(widget, row, col, row_span, col_span, alignment)



class Banner(WidgetBase):

    """Base class for a banner.
    """

    def __init__(self, width, height):
        """Constructor.
        """
        super().__init__(column_stretch={1: 1}, background='white')
        self.setFixedSize(width, height)
        self.layout().setContentsMargins(0, 0, 0, 0)



class RosterHeader(Banner):

    """
    """

    def __init__(self, width, height):
        """Constructor.
        """
        super().__init__(width, height)
        self.text_label = QLabel()
        self.text_label.setFixedSize(width, height)
        self.text_label.setWordWrap(True)
        self.text_label.setIndent(20)
        self.text_label.setAlignment(Qt.AlignLeft)
        self.add_widget(self.text_label, 0, 1)

    def set_roster(self, roster, current_poster_id):
        """
        """
        text = f'<font color="black" size="4">{roster.session}</font><br/><br/>'
        for i, poster in enumerate(roster):
            if i == current_poster_id:
                text += f'<font color="black" size="2">{poster}</font><br/>'
            else:
                text += f'<font color="gray" size="2">{poster}</font><br/>'
        self.text_label.setText(text)



class PosterHeader(Banner):

    """Class describing the poster header.
    """

    def __init__(self, width, height):
        """Constructor.
        """
        super().__init__(width, height)
        self.height = height
        self.presenter_label = QLabel()
        self.presenter_label.setFixedSize(height, height)
        self.text_label = QLabel()
        self.text_label.setFixedSize(width, height)
        self.text_label.setWordWrap(True)
        self.text_label.setIndent(20)
        self.qrcode_label = QLabel()
        self.qrcode_label.setFixedSize(height, height)
        qrcode = QPixmap('posters/qrcode.png').scaledToHeight(height, Qt.SmoothTransformation)
        self.qrcode_label.setPixmap(qrcode)
        self.add_widget(self.presenter_label, 0, 0)
        self.add_widget(self.text_label, 0, 1)
        self.add_widget(self.qrcode_label, 0, 2)

    def set_poster(self, poster):
        """
        """
        presenter = poster.presenter
        try:
            self.presenter_label.setPixmap(poster.presenter_pixmap)
        except TypeError:
            self.presenter_label.clear()
        text = f'<font color="black" size="4">{presenter.full_name()}</font><br/>'\
               f'<font color="gray" size="2">{presenter.affiliation}</font><br/>'
        self.text_label.setText(text)



class Footer(Banner):

    """Class describing the footer for the slideshow.
    """

    def __init__(self, width, height, parent=None):
        """Constructor.
        """
        super().__init__(width, height)
        self.parent = parent
        self.text_label = QLabel()
        self.text_label.setFixedSize(width, height)
        self.text_label.setMargin(10)
        self.add_widget(self.text_label, 0, 1)

    def update(self):
        """
        """
        t = int(self.parent.timer.remainingTime() / 1000. + 0.9)
        text = f'<font color="gray" size="2">Status: running, {t} s to the next poster</font><br/>'
        self.text_label.setText(text)



class SlideShow(WidgetBase):

    """Basic slideshow class.
    """

    DEFAULT_ADVANCE_INTERVAL = 30.
    DEFAULT_PAUSE_INTERVAL = 120.
    WINDOW_TITLE = '15th Pisa Meeting on Advanced Detectors'
    VALID_GEOMETRIES = ('default', 'maximize', 'fullscreen')

    def __init__(self, folder_path: str, **kwargs):
        """Constructor.
        """
        super().__init__(column_stretch={0: 1, 1: 100, 2: 1}, **kwargs)
        self.folder_path = folder_path
        self.screen_id = read_screen_id()
        # Parse the command-line arguments.
        advance_interval = kwargs.get('advance', self.DEFAULT_ADVANCE_INTERVAL)
        pause_interval = kwargs.get('pause', self.DEFAULT_PAUSE_INTERVAL)
        geometry = kwargs.get('geometry')
        assert geometry in self.VALID_GEOMETRIES
        # Convert times from s to msec.
        self.advance_interval = self.sec_to_msec(advance_interval)
        self.pause_interval = self.sec_to_msec(pause_interval)
        # Setup the widget.
        poster_size = (kwargs.get('poster_width'), kwargs.get('poster_height'))

        self.poster_label = QLabel()
        self.roster_header = RosterHeader(kwargs.get('poster_width'), kwargs.get('roster_header_height', 50))
        self.poster_header = PosterHeader(kwargs.get('poster_width'), kwargs.get('poster_header_height', 70))
        self.footer = Footer(kwargs.get('poster_width'), kwargs.get('footer_height', 40), self)
        self.fading_effect = FadingEffect()
        self.poster_label.setGraphicsEffect(self.fading_effect)
        self.add_widget(self.roster_header, 0, 1)
        self.add_widget(self.poster_header, 1, 1)
        self.add_widget(self.poster_label, 2, 1)
        self.add_widget(self.footer, 3, 1)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance)
        self.footer_timer = QTimer()
        self.footer_timer.timeout.connect(self.footer.update)
        self.footer_timer.start(100)
        # We're good to go!
        self.timer.start(self.advance_interval)
        if geometry == 'maximize':
            self.showMaximized()
        elif geometry == 'fullscreen':
            self.showFullScreen()
        else:
            self.show()
        #
        config_file_path = kwargs.get('cfgfile')
        root_folder_path = os.path.dirname(config_file_path)
        self.poster_roster = PosterRoster(config_file_path, root_folder_path, self.screen_id)
        self.poster_roster.load_poster_data(poster_size, self.poster_header.height)
        self.display_poster(0)

    def display_poster(self, index: int = 0) -> None:
        """Display a given poster.
        """
        self.__current_index = index % len(self.poster_roster)
        self.roster_header.set_roster(self.poster_roster, self.__current_index)
        poster = self.poster_roster[self.__current_index]
        self.poster_header.set_poster(poster)
        next_id = (self.__current_index + 1) % len(self.poster_roster)
        next_poster = self.poster_roster[next_id]
        self.poster_label.setPixmap(poster.poster_pixmap)
        self.fading_effect.fade_in()

    def advance(self) -> None:
        """Advance to the next image.
        """
        self.display_poster(self.__current_index + 1)

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

    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #     """Overloaded method to handle key events.
    #     """
    #     # pylint: disable=invalid-name
    #     print(event.text())
    #     index = self.pixmap_list.pixmap_index(event.text())
    #     if index is None:
    #         return
    #     self.display_image(index)
    #     self.timer.stop()
    #     self.timer.singleShot(self.pause_interval, self.timer.start)
