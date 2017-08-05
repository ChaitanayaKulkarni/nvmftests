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
NVMF Create/Delete Host, Target :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Delete Host.
    4. Delete Target.
"""

from loopback import Loopback
from nvmf_test import NVMFTest
from target import NVMFTarget
from host import NVMFHost
from nose.tools import assert_equal


class TestNVMFCreateDeleteFabric(NVMFTest):

    """ Represents Create Delete target and host testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.loopdev = None
        self.host_subsys = None
        self.target_subsys = None

        self.setup_log_dir(self.__class__.__name__)
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_loop_dev)

    def setUp(self):
        print("configuering loopback")
        self.loopdev.init()

    def tearDown(self):
        print("deleting loopback")
        self.loopdev.delete()

    def test_create_delete_fabric(self):
        """ Testcase main """
        target_type = "loop"

        self.target_subsys = NVMFTarget(target_type)
        ret = self.target_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : config target failed")

        self.host_subsys = NVMFHost(target_type)
        ret = self.host_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : config host failed")

        ret = self.host_subsys.delete()
        assert_equal(ret, True, "ERROR : delete host subsystems failed")

        ret = self.target_subsys.delete()
        assert_equal(ret, True, "ERROR : delete target subsystems failed")
