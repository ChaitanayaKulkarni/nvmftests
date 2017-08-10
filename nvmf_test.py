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
""" Base Class for all NVMF testcases.
"""

import os
import sys
import json
from nose.tools import assert_equal

from utils.const import Const
from utils.diskio import DD
from utils.diskio import FIO
from target import NVMFTarget
from host import NVMFHost
from target_config_generator import target_config
from nvmf_test_logger import NVMFLogger


def __dd_worker__(iocfg):
    """ dd worker thread function.
        - Args :
              - iocfg : io configuration.
        - Returns :
              - Return value of dd command.
    """
    return DD.run_io(iocfg)


def __fio_worker__(iocfg):
    """ fio worker thread function.
        - Args :
              - iocfg : io configuration.
        - Returns :
              - Return value of fio command.
    """
    return FIO.run_io(iocfg)


class NVMFTest(object):

    """ Common attributes for all testcases """

    def __init__(self):
        self.config_file = 'nvmftests.json'
        self.data_size = Const.ZERO
        self.block_size = Const.ZERO
        self.nr_dev = Const.ZERO
        self.mount_path = Const.XXX
        self.test_log_dir = Const.XXX
        self.nr_dev = Const.ZERO
        self.nr_target_subsys = Const.ZERO
        self.nr_ns_per_subsys = Const.ZERO
        self.target_config_file = Const.XXX
        self.loopdev = None
        self.host_subsys = None
        self.target_subsys = None
        self.log_dir = './logs/' + self.__class__.__name__ + '/'
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

        self.load_config()
        self.fio_read = {'IO_TYPE': 'fio',
                         'group_reporting': '1',
                         'rw': 'randread',
                         'bs': '4k',
                         'numjobs': '4',
                         'iodepth': '8',
                         'runtime': '30',
                         'loop': '1',
                         'ioengine': 'libaio',
                         'direct': '1',
                         'invalidate': '1',
                         'randrepeat': '1',
                         'size': '100M',
                         'filename': Const.XXX,
                         'name': 'test1',
                         'THREAD': __fio_worker__,
                         'RC': '0'}

        self.fio_fs_write = {'IO_TYPE': 'fio',
                             'group_reporting': '1',
                             'rw': 'randwrite',
                             'bs': '4k',
                             'numjobs': '4',
                             'iodepth': '8',
                             'runtime': '30',
                             'loop': '1',
                             'ioengine': 'libaio',
                             'direct': '1',
                             'invalidate': '1',
                             'randrepeat': '1',
                             'size': '10M',
                             'directory': Const.XXX,
                             'name': 'test1',
                             'THREAD': __fio_worker__,
                             'RC': '0'}

        self.dd_read = {'IO_TYPE': 'dd',
                        'IODIR': 'read',
                        'THREAD': __dd_worker__,
                        'IF': None,
                        'OF': '/dev/null',
                        'BS': '4K',
                        'COUNT': str(self.data_size / self.block_size),
                        'RC': 0}

        self.dd_write = {'IO_TYPE': 'dd',
                         'IODIR': 'write',
                         'THREAD': __dd_worker__,
                         'IF': '/dev/zero',
                         'OF': None,
                         'BS': '4K',
                         'COUNT': str(self.data_size / self.block_size),
                         'RC': 0}

    def build_target_config(self, dev_list):
        """ Generates target config file in JSON format from test config file.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        with open(self.config_file) as cfg_file:
            cfg = json.load(cfg_file)
            self.nr_dev = int(cfg['nr_dev'])
            self.nr_target_subsys = int(cfg['nr_target_subsys'])
            self.nr_ns_per_subsys = int(cfg['nr_ns_per_subsys'])
            self.target_config_file = cfg['target_config_file']

            target_cfg = target_config(self.target_config_file,
                                       self.nr_target_subsys,
                                       self.nr_ns_per_subsys,
                                       dev_list)
            target_cfg.build_target_subsys()

    def load_config(self):
        """ Load Basic test configuration.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        with open(self.config_file) as nvmftest_config:
            config = json.load(nvmftest_config)
            self.mount_path = config['mount_path']
            self.data_size = self.human_to_bytes(config['data_size'])
            self.block_size = self.human_to_bytes(config['block_size'])
            self.nr_dev = int(config['nr_dev'])
            return True

        return False

    def human_to_bytes(self, num_str):
        """ Converts num_str from human redable format to bytes.
            Args :
                - num_str : human redable string.
            Returns :
                - On success decimal equivalant of num_str, 0 on failure.
        """
        decimal_bytes = 0
        num_suffix = str(num_str[-2:]).upper()
        if num_suffix == Const.KB:
            decimal_bytes = int(num_str.split("K")[0]) * Const.ONE_KB
        elif num_suffix == Const.MB:
            decimal_bytes = int(num_str.split("M")[0]) * Const.ONE_MB
        elif num_suffix == Const.GB:
            decimal_bytes = int(num_str.split("G")[0]) * Const.ONE_GB
        else:
            print(self.err_str + "invalid suffix " + num_str)

        return decimal_bytes

    def setup_log_dir(self, test_name):
        """ Set up the log directory for a testcase.
            Args :
                - test_name : name of the testcase.
            Returns :
                - None.
        """
        self.test_log_dir = self.log_dir + "/" + test_name
        if not os.path.exists(self.test_log_dir):
            os.makedirs(self.test_log_dir)
        sys.stdout = NVMFLogger(self.test_log_dir + "/" + "stdout.log")
        sys.stderr = NVMFLogger(self.test_log_dir + "/" + "stderr.log")

    def common_setup(self):
        """ Common test case setup function.
            Args :
                - test_name : name of the testcase.
            Returns :
                - None.
        """
        target_type = 'loop'
        self.target_subsys = NVMFTarget(target_type)
        ret = self.target_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : target config failed")
        self.host_subsys = NVMFHost(target_type)
        ret = self.host_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : host config failed")

    def common_tear_down(self):
        """ Common test case tear down function.
            Args :
                - test_name : name of the testcase.
            Returns :
                - None.
        """
        self.host_subsys.delete()
        self.target_subsys.delete()
