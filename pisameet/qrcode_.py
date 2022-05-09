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

"""QR-code facilities.
"""

import qrcode

from pisameet import MISSING_QRCODE_PATH


def generate_qrcode(data, file_path):
    """Generate a qrcode for a given input data.
    """
    #pylint: disable=invalid-name
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(file_path)



if __name__ == '__main__':
    generate_qrcode('Ops... something went wrong?', MISSING_QRCODE_PATH)