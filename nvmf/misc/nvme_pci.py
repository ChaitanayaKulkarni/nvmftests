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
""" Represents NVMe PCIe block device.
"""
import os
import re
import sys
import time
import logging
from natsort import natsorted

sys.path.append('../../')
from utils.shell import Cmd


class NVMePCIeBlk(object):
    """
    Represents NVMe PCIe block devices.

        - Attributes :
            - nr_devices : max null block devices.
            - dev_list : list of null devices.
    """
    def __init__(self):
        self.nr_devices = None
        self.ctrl_list = []
        self.dev_list = []
        self.logger = logging.getLogger(__name__)
        self.log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        self.log_format += '%(filename)20s %(funcName)20s %(lineno)4d'
        self.log_format += '%(pathname)s'
        self.formatter = logging.Formatter(self.log_format)
        self.logger.setLevel(logging.WARNING)

        Cmd.exec_cmd("modprobe -r nvme")
        Cmd.exec_cmd("modprobe nvme")
        # allow devices to appear in /dev
        time.sleep(1)

    def init(self):
        """ Create and initialize Loopback.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ctrl = "XXX "
        try:
            dev_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err) + ".")
            return None, None
        dev_list = natsorted(dev_list, key=lambda y: y.lower())
        pat = re.compile("^nvme[0-9]+$")
        for line in dev_list:
            line = line.strip('\n')
            if pat.match(line):
                ctrl = line
                self.ctrl_list.append("/dev/" + ctrl)

        # find namespace(s) associated with ctrl
        try:
            dir_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err))
            return None, None
        pat = re.compile("^" + ctrl + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                self.logger.info("Generated namespace name /dev/" + line + ".")
                self.dev_list.append("/dev/" + line)

        self.logger.info(self.ctrl_list)
        self.logger.info(self.dev_list)
        return True

    def delete(self):
        """ Delete this Loopback.
            - Args :
                  - None.
            -Returns :
                  - True on success, False on failure.
        """
        Cmd.exec_cmd("modprobe -qr nvme")
        return True
