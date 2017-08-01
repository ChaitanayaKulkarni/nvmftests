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
"""
NVMeOF host template :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Write testcase code here.
    4. Delete Host.
    5. Delete Target.
"""

import time
from loopback import Loopback
from nvmf_test import NVMeOFTest
from target import NVMeOFTarget
from host import NVMeOFHost
from nose.tools import assert_equal


class TestNVMFHostTemplate(NVMeOFTest):

    """ Represents host template testcase """

    def __init__(self):
        NVMeOFTest.__init__(self)
        self.loopdev = None
        self.host_subsys = None
        self.target_subsys = None

        self.setup_log_dir(self.__class__.__name__)
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_loop_dev)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev.init()
        target_type = "loop"
        self.target_subsys = NVMeOFTarget(target_type)
        ret = self.target_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : target config failed")
        self.host_subsys = NVMeOFHost(target_type)
        ret = self.host_subsys.config(self.target_config_file)
        assert_equal(ret, True, "ERROR : host config failed")

    def tearDown(self):
        """ Post section of testcase """
        self.host_subsys.delete()
        self.target_subsys.delete()
        self.loopdev.delete()

    def disable_target_ns(self):
        ret = True
        for target_subsys in iter(self.target_subsys):
            try:
                print("Target Subsystem NQN " + target_subsys.nqn)
                for target_ns in iter(target_subsys):
                    try:
                        ns_path = target_ns.ns_path
                        print(" Target NS ID " + str(target_ns.ns_id))
                        print(" Disabling Target NS Path " + ns_path)
                        if target_ns.disable():
                            print("ERROR : failed to disable ns " + ns_path)
                            ret = False
                    except StopIteration:
                        break
            except StopIteration:
                break
        return ret

    def test_host(self):
        """ Testcase main """
        self.host_subsys.run_traffic_parallel(self.dd_read_traffic)
        time.sleep(5)
        ret = self.disable_target_ns()
        assert_equal(ret, True, "ERROR : target ns disable failed")
        self.host_subsys.wait_traffic_parallel()
