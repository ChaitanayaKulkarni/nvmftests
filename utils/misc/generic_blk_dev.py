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
""" Represents generic block device.
"""

import os
import stat
import logging

from utils.log import Log


class GenBlk(object):
    """
    Represents Generic BLK block devices.

        - Attributes:
            - nr_devices : max block devices.
            - dev_list : list of block devices.
    """
    def __init__(self, nr_devices):
        self.nr_devices = str(nr_devices)
        self.dev_list = []
        self.logger = Log.get_logger(__name__, 'gen_blk')
        self.logger.setLevel(logging.DEBUG)

    def init(self, dev_list):
        """ Create and initialize Generic Block Device.
            - Args :
                - dev_list : list of block devices.
            - Returns :
                - True on success, False on failure.
        """
        for i in range(0, int(self.nr_devices)):
            self.logger.info(dev_list[i])
            if stat.S_ISBLK(os.stat(dev_list[i]).st_mode) is False:
                self.logger.error("block device not found " + dev_list[i])
                return False
            self.dev_list.append(dev_list[i])
        self.logger.info(self.dev_list)
        return True
