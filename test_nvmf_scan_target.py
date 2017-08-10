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
NVMF scan target :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Scan target subsystem.
    4. Delete Host.
    5. Delete Target.
"""


from nose.tools import assert_equal
from loopback import Loopback
from nvmf_test import NVMFTest


class TestNVMFScanTarget(NVMFTest):

    """ Represents scan target subsystems testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.setup_log_dir(self.__class__.__name__)
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_dev)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev.init()
        self.build_target_config(self.loopdev.dev_list)
        super(TestNVMFScanTarget, self).common_setup()

    def tearDown(self):
        """ Post section of testcase """
        super(TestNVMFScanTarget, self).common_tear_down()
        self.loopdev.delete()

    def test_scan_target(self):
        """ Testcase main """
        success = True
        for target_subsys in iter(self.target_subsys):
            try:
                print("Target Subsystem NQN " + target_subsys.nqn)
                for target_ns in iter(target_subsys):
                    try:
                        print(" Target NS ID " + str(target_ns.ns_id))
                        print(" Target NS Path " + target_ns.ns_path)
                    except StopIteration:
                        success = False
                        break
            except StopIteration:
                success = False
                break

        assert_equal(success, True, "ERROR : failed to scan target")
