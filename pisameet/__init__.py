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


"""Program-wise facilities.
"""


import logging


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
