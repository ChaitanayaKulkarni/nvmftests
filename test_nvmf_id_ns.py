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
NVMeOF test id-ns on each namespace :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Execute id-ns namespaces.
    4. Delete Host.
    5. Delete Target.
"""

from loopback import Loopback
from nvmf_test import NVMeOFTest
from target import NVMeOFTarget
from host import NVMeOFHost
from nose.tools import assert_equal


class TestNVMFIdentifyNamespace(NVMeOFTest):

    """ Represents Identify Namespace Test testcase """

    def __init__(self):
        NVMeOFTest.__init__(self)
        self.loopdev = None
        self.host_subsys = None
        self.target_subsys = None

        self.setup_log_dir(self.__class__.__name__)
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_devices)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev.init_loopback()
        target_type = "loop"
        self.target_subsys = NVMeOFTarget(target_type)
        self.target_subsys.config()
        self.host_subsys = NVMeOFHost(target_type)
        self.host_subsys.config()

    def tearDown(self):
        """ Post section of testcase """
        self.host_subsys.delete()
        self.target_subsys.delete()
        self.loopdev.del_loopback()

    def test_identify_namespace(self):
        """ Testcase main """
        ret = self.host_subsys.id_ns()
        assert_equal(ret, True, "ERROR : id ns failed.")
