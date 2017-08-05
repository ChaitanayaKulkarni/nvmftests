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

from utils.shell import Cmd
from utils.const import Const


class Loopback(object):
    """
    Represents Loopback driver block devices.

        - Attributes :
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
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

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
        count = self.dev_size / self.block_size

        for i in range(Const.ZERO, self.max_loop):
            dev = self.path + "/test" + str(i)
            cmd = "dd if=/dev/zero of=" + dev + \
                " count=" + str(count) + " bs=" + str(self.block_size)
            print(cmd)
            ret = Cmd.exec_cmd(cmd)
            if ret is False:
                print(self.err_str + " file creation " + self.dev_list[i])
                self.delete()
                return False
            cmd = "losetup /dev/loop" + str(i) + " " + dev
            print(cmd)
            if Cmd.exec_cmd(cmd) is False:
                print(self.err_str + cmd + " failed.")
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
        loop_cnt = Const.ZERO
        for i in self.dev_list:
            cmd = "losetup -d /dev/loop" + str(loop_cnt)
            print(cmd)
            Cmd.exec_cmd(cmd)
            os.remove(i)
            loop_cnt += Const.ONE

        Cmd.exec_cmd("modprobe -qr loop")
        return ret
