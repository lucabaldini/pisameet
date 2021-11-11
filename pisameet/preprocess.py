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

"""Pre-processing tools.
"""


import glob
import os
import subprocess


def crawl(folder_path: str, file_type: str = '.pdf', filter_pattern: str = None) -> list:
    """Crawl a given folder recursively and return a list of all the files of
    a given type matching a given pattern.

    Arguments
    ---------
    folder_path : str
        The path to the root folder to be recursively crawled.

    file_type : str
        The file extension, including the dot (e.g., '.pdf')

    filter_pattern : str
        An optional filtering pattern---if not None, only the files containing
        the pattern in the name are retained.

    Return
    ------
    A list of absolute file paths.
    """
    file_list = []
    for root, subdirs, files in os.walk(folder_path):
        file_list += [os.path.join(root, file) for file in files if file.endswith(file_type)]
    file_list.sort()
    if filter_pattern is not None:
        file_list = [file_path for file_path in file_list if filter_pattern in os.path.basename(file_path)]
    return file_list


def pdf_to_png(input_file_path: str, output_folder_path) -> str:
    """Convert a .pdf file to a .png file.
    """
    assert input_file_path.endswith('.pdf')
    file_name = os.path.basename(input_file_path).replace('.pdf', '.png')
    output_file_path = os.path.join(output_folder_path, file_name)
    print('Converting %s to %s...' % (input_file_path, output_file_path))
    subprocess.run(['convert', input_file_path, output_file_path])
    return output_file_path


def crawl_pm2018(folder_path: str) -> list:
    """Crawl the 2018 Pisa meeting material folder and return a dictionary of
    file paths, organized by session.
    """
    file_list = crawl(folder_path, '.pdf', 'Poster')
    file_dict = {}
    for file_path in file_list:
        session_name = file_path.split(os.sep)[-3].replace('_-_Poster_Session', '')
        if session_name in file_dict:
            file_dict[session_name].append(file_path)
        else:
            file_dict[session_name] = [file_path]
    return file_dict


def convert_pm2018(input_folder_path, output_folder_path):
    """Convert all the pdf files of the 2018 Pisa meeting to png format.
    """
    for session_name, file_list in crawl_pm2018(input_folder_path).items():
        _output_folder = os.path.join(output_folder_path, session_name)
        os.makedirs(_output_folder)
        for file_path in file_list:
            pdf_to_png(file_path, _output_folder)




if __name__ == '__main__':
    convert_pm2018('/data/work/pm2018_material/', '/home/data/work/pm2018_posters')
