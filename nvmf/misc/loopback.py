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
""" Represents Loopback block devices.
"""

import os
import logging

from utils.shell import Cmd


class Loopback(object):
    """
    Represents Loopback driver block devices.

        - Attributes:
            - path : path to create backend files.
            - dev_size : device file size.
            - block size : block size to create file.
            - max_loop : max loop devices.
            - dev_list : list of loop back files.
    """
    def __init__(self, path, dev_size, block_size, max_loop):
        self.path = path
        self.dev_size = dev_size
        self.block_size = block_size
        self.max_loop = max_loop
        self.dev_list = []
        self.logger = logging.getLogger(__name__)
        self.log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        self.log_format += '%(filename)20s %(funcName)20s %(lineno)4d'
        self.log_format += '%(pathname)s'
        self.formatter = logging.Formatter(self.log_format)
        self.logger.setLevel(logging.DEBUG)

        Cmd.exec_cmd("losetup -D")
        Cmd.exec_cmd("modprobe -qr loop")
        Cmd.exec_cmd("modprobe loop max_loop=" + str(max_loop))

    def init(self):
        """ Create and initialize Loopback.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        if self.dev_size == 0 or self.block_size == 0:
            self.logger.err("invalid device size or block size")
            return False

        count = self.dev_size / self.block_size

        for i in range(0, self.max_loop):
            file_path = self.path + "/test" + str(i)
            cmd = "dd if=/dev/zero of=" + file_path + \
                " count=" + str(count) + " bs=" + str(self.block_size)
            self.logger.info(cmd)
            ret = Cmd.exec_cmd(cmd)
            if ret is False:
                self.logger.error("lookback file creation " + self.dev_list[i])
                self.delete()
                return False
            dev = "/dev/loop" + str(i)
            cmd = "losetup " + dev + " " + file_path
            self.logger.info(cmd)
            if Cmd.exec_cmd(cmd) is False:
                self.logger.error(cmd + " failed.")
                return False

            self.dev_list.append(dev)
        return True

    def delete(self):
        """ Delete this Loopback.
            - Args :
                - None.
            -Returns :
                - True on success, False on failure.
        """
        ret = True
        loop_cnt = 0
        for i in self.dev_list:
            cmd = "losetup -d /dev/loop" + str(loop_cnt)
            self.logger.info(cmd)
            Cmd.exec_cmd(cmd)
            file_path = self.path + "/test" + str(loop_cnt)
            os.remove(file_path)
            loop_cnt += 1

        Cmd.exec_cmd("modprobe -qr loop")
        return ret
