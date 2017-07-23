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
""" Base Class for all NVMeOF testcases.
"""

import os
import sys
import json

from utils.const import Const
from utils.diskio import DD
from nvmf_test_logger import NVMeOFLogger


def __dd_worker__(iocfg):
    """ dd worker thread function.
        - Args :
                - iocfg : io configuration.
        - Returns :
                - None.
    """
    return DD.run_io(iocfg)


class NVMeOFTest(object):

    def __init__(self):
        self.config_file = 'nvmftests.json'
        self.data_size = Const.ZERO
        self.block_size = Const.ZERO
        self.nr_devices = Const.ZERO
        self.mount_path = Const.XXX
        self.test_log_dir = Const.XXX
        self.log_dir = "./logs/" + self.__class__.__name__ + "/"

        self.load_config()

        self.dd_read = {"IODIR": "read",
                        "THREAD": __dd_worker__,
                        "IF": None,
                        "OF": "/dev/null",
                        "BS": "4K",
                        "COUNT": str(self.data_size / self.block_size),
                        "RC": 0}

        self.dd_write = {"IODIR": "write",
                         "THREAD": __dd_worker__,
                         "IF": "/dev/zero",
                         "OF": None,
                         "BS": "4K",
                         "COUNT": str(self.data_size / self.block_size),
                         "RC": 0}

    def load_config(self):
        """ Load Basic test configuration.
            - Args:
                - None
            - Returns:
                - None
        """
        with open(self.config_file) as nvmftest_config:
            config = json.load(nvmftest_config)
            self.mount_path = config['mount_path']
            self.data_size = self.human_to_bytes(config['data_size'])
            self.block_size = self.human_to_bytes(config['block_size'])
            self.nr_devices = int(config['nr_devices'])

            print("dev_size %d block_size %d nr_devices %d", (self.data_size, self.block_size, self.nr_devices))

    def human_to_bytes(self, num_str):
        """ Converts num_str from human redable format to decimal
            Args:
              - num_str : human redable string.
            Returns:
              - On success decimal equivalant of num_str, 0 on failure
        """
        no = 0
        num_suffix = str(num_str[-2:]).upper()
        if num_suffix == Const.KB:
            no = int(num_str.split("K")[0]) * Const.ONE_KB
        elif num_suffix == Const.MB:
            no = int(num_str.split("M")[0]) * Const.ONE_MB
        elif num_suffix == Const.GB:
            no = int(num_str.split("G")[0]) * Const.ONE_GB
        else:
            print(self.err_str + "invalid suffix " + num_str)

        return no

    def setup_log_dir(self, test_name):
        """ Set up the log directory for a testcase
            Args:
              - test_name : name of the testcase.
            Returns:
              - None
        """
        self.test_log_dir = self.log_dir + "/" + test_name
        if not os.path.exists(self.test_log_dir):
            os.makedirs(self.test_log_dir)
        sys.stdout = NVMeOFLogger(self.test_log_dir + "/" + "stdout.log")
        sys.stderr = NVMeOFLogger(self.test_log_dir + "/" + "stderr.log")
