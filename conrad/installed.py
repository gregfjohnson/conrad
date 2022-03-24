"""
Replacement for pip.get_installed_distributions(),
which is no longer in pip.
Uses the command-line call "pip3 list".
"""
"""
Copyright 2016 Baris Ungun, Anqi Fu

This file is part of CONRAD.

CONRAD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CONRAD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CONRAD.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import re

def module_installed(name, version_string=None):
    """
    Test whether queried module is installed.

    Arguments:
        name (:obj:`str`): Name of module to query.
        version_string (:obj:`str`, optional): Specific module version
            to query.

    Returns:
        :obj:`bool`: ``True`` if queried module has a matching string in
        dictionary values returned by
        :func:`pip.get_installed_distributions`.
    """

    stream = os.popen('pip3 list')

    output = stream.read()
    output = str.split(output, '\n')
    tbl = {}
    for line in output:
        ppp = re.match('([^ ]*) *([^ ]*) *', line)
        if ppp:
            name = ppp[1]
            version = ppp[2]

            tbl[name] = version

    result = True

    if not name in tbl.keys():
        result = False

    elif version_string:
        result = version_string == tbl[name_ver[0]]

    return result

if True:
    print(module_installed('ufw'))
