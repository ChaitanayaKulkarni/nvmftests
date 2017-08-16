# Copyright (c) 2016-2017 Western Digital Corporation or its affiliates.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.
#
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@hgst.com>
#
""" Represents DD(1) wrapper
"""

import subprocess


class DD(object):

    """
    Represents dd command wrapper.
    """

    @staticmethod
    def run_io(iocfg):
        """ Executes dd command based on the config argument.
            - Args :
                  - IO Configuration for dd command.
            - Returns :
                  - True on success, False on failure.
        """
        cmd = "dd if=" + iocfg['IF'] + " of=" + iocfg['OF'] + \
            " bs=" + iocfg['BS'] + " count=" + iocfg['COUNT'] + \
            " > /tmp/op 2>&1"

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        ret = True
        rc = proc.wait()
        if rc != iocfg['RC']:
            ret = False

        return ret
