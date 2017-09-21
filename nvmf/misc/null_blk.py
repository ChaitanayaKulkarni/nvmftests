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
#   Author: Chaitanya Kulkarni <chaitanya.kulkarni@wdc.com>
#
""" Represents null block device.
"""
import sys
import logging

sys.path.append('../../')
from utils.shell import Cmd


class NullBlk(object):
    """
    Represents Null BLK driver block devices.

        - Attributes :
            - dev_size : device file size.
            - block size : block size to create file.
            - nr_devices : max null block devices.
            - dev_list : list of null devices.
    """
    def __init__(self, dev_size, block_size, nr_devices):
        self.dev_size = str(dev_size)
        self.block_size = str(block_size)
        self.nr_devices = str(nr_devices)
        self.dev_list = []
        self.logger = logging.getLogger(__name__)
        self.log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        self.log_format += '%(filename)20s %(funcName)20s %(lineno)4d'
        self.log_format += '%(pathname)s'
        self.formatter = logging.Formatter(self.log_format)
        self.logger.setLevel(logging.WARNING)

        cmd = "modprobe null_blk gb=" + self.dev_size
        cmd += " bs=" + self.block_size + " nr_devices=" + self.nr_devices
        Cmd.exec_cmd("modprobe -r null_blk")
        Cmd.exec_cmd(cmd)

    def init(self):
        """ Create and initialize null blk.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        for i in range(0, int(self.nr_devices)):
            self.logger.info("/dev/nullb" + str(i))
            self.dev_list.append("/dev/nullb" + str(i))

        self.logger.info(self.dev_list)
        return True

    def delete(self):
        """ Delete this null blk.
            - Args :
                  - None.
            -Returns :
                  - True on success, False on failure.
        """
        Cmd.exec_cmd("modprobe -qr null_blk")
        return True
