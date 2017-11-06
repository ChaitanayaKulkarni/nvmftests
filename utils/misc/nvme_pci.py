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
from natsort import natsorted

sys.path.append('../../')
from utils.shell import Cmd
from utils.log import Log


class NVMePCIeBlk(object):
    """
    Represents NVMe PCIe block devices.

        - Attributes :
            - nr_devices : number of block devices.
            - ctrl_list : NVMe PCIe controller list.
            - dev_list : list of devices.
    """
    def __init__(self):
        self.nr_devices = None
        self.ctrl_list = []
        self.dev_list = []
        self.logger = Log.get_logger(__name__, 'nvme_pci')

        Cmd.exec_cmd("modprobe -r nvme")
        Cmd.exec_cmd("modprobe nvme")
        # allow devices to appear in /dev/
        time.sleep(1)

    def is_pci_ctrl(self, ctrl):
        """ Validate underlaying device belongs to pci subsystem.
            - Args :
                - None.
            - Returns :
                - True if device is belongs to PCIe subsystem, False otherwise.
        """
        cmd = "find /sys/devices -name " + ctrl + " | grep -i pci"
        return Cmd.exec_cmd(cmd)

    def init(self):
        """ Build the list of NVMe PCIe controllers.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        time.sleep(1)
        ctrl = "XXX "
        try:
            dev_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err) + ".")
            return False
        dev_list = natsorted(dev_list, key=lambda y: y.lower())
        pat = re.compile("^nvme[0-9]+$")
        for line in dev_list:
            line = line.strip('\n')
            if pat.match(line):
                ctrl = line
                ctrl_dev = "/dev/" + ctrl
                if self.is_pci_ctrl(ctrl) is True:
                    self.logger.info("found NVMe PCIe Controller " + ctrl_dev)
                    self.ctrl_list.append(ctrl_dev)
                else:
                    self.logger.info(ctrl_dev + " is not pci ctrl.")

        # find namespace(s) associated with ctrl
        try:
            dir_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err))
            return False
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
        """ Remove the nvme module.
            - Args :
                - None.
            -Returns :
                - True on success, False on failure.
        """
        return Cmd.exec_cmd("modprobe -qr nvme")
