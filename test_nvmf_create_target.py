# Copyright (c) 2015-2016 Western Digital Corporation or its affiliates.
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
"""
NVMeOF Create/Delete Target :-

    1. From the config file create Target.
    2. Delete Target.
"""

from loopback import Loopback
from nvmf_test import NVMeOFTest
from target import NVMeOFTarget
from nose.tools import assert_equal


class TestNVMFCreateTarget(NVMeOFTest):

    """ Represents Create Delete Target testcase """

    def __init__(self):
        NVMeOFTest.__init__(self)
        self.target_subsys = None
        self.loopdev = None
        self.setup_log_dir(self.__class__.__name__)
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_devices)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev.init()
        target_type = "loop"
        self.target_subsys = NVMeOFTarget(target_type)

    def tearDown(self):
        """ Post section of testcase """
        self.target_subsys.delete()
        self.loopdev.delete()

    def test_create_target(self):
        """ Testcase main """
        ret = self.target_subsys.config()
        assert_equal(ret, True, "ERROR : config target failed.")
