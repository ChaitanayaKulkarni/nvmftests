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
"""
NVMF test mkfs on each subsystem :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Execute mkfs on all host namespaces.
    4. Delete Host.
    5. Delete Target.
"""


import sys
from nose.tools import assert_equal
sys.path.append("../")
from nvmf.misc.loopback import Loopback
from nvmf_test import NVMFTest


class TestNVMFMKFS(NVMFTest):

    """ Represents mkfs testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.setup_log_dir(self.__class__.__name__)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_dev)
        self.loopdev.init()
        print self.loopdev.dev_list
        self.build_target_config(self.loopdev.dev_list)
        super(TestNVMFMKFS, self).common_setup()

    def tearDown(self):
        """ Post section of testcase """
        super(TestNVMFMKFS, self).common_tear_down()
        self.loopdev.delete()

    def test_mkfs(self):
        """ Testcase main """
        print("Now Running " + self.__class__.__name__)
        ret = self.host_subsys.mkfs_seq("ext4")
        assert_equal(ret, True, "ERROR : mkfs failed.")
        ret = self.host_subsys.run_fs_ios(self.fio_fs_write)
        assert_equal(ret, True, "ERROR : fio failed.")
