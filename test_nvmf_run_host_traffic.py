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
NVMF run host traffic and disable target namespace(s) :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Start host traffic parallely on all host ns, disable target ns.
    4. Delete Host.
    5. Delete Target.
"""


import time
from nose.tools import assert_equal
from utils.diskio import DD
from loopback import Loopback
from nvmf_test import NVMFTest


def __run_traffic__(iocfg):
    """ dd worker thread function to run IOs until it fails.
        - Args :
              - iocfg : io configuration.
        - Returns :
              - True when dd command fails.
    """
    print("Run traffic :- ")
    while True:
        ret = DD.run_io(iocfg)
        if ret is False:
            return True


class TestNVMFHostTraffic(NVMFTest):

    """ Represents disable target namespace(s) while host traffic is running
        testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.setup_log_dir(self.__class__.__name__)

    def setUp(self):
        """ Pre section of testcase """
        self.loopdev = Loopback(self.mount_path, self.data_size,
                                self.block_size, self.nr_dev)
        self.loopdev.init()
        self.build_target_config(self.loopdev.dev_list)
        self.dd_read_traffic = {"IO_TYPE": "dd",
                                "IODIR": "read",
                                "THREAD": __run_traffic__,
                                "IF": None,
                                "OF": "/dev/null",
                                "BS": "4K",
                                "COUNT": str(self.data_size / self.block_size),
                                "RC": 0}
        super(TestNVMFHostTraffic, self).common_setup()

    def tearDown(self):
        """ Post section of testcase """
        super(TestNVMFHostTraffic, self).common_tear_down()
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
                        if target_ns.disable() is False:
                            print("ERROR : failed to disable ns " + ns_path)
                            ret = False
                    except StopIteration:
                        break
            except StopIteration:
                break
        return ret

    def test_host_traffic(self):
        """ Testcase main """
        self.host_subsys.run_traffic_parallel(self.dd_read_traffic)
        time.sleep(5)
        ret = self.disable_target_ns()
        assert_equal(ret, True, "ERROR : target ns disable failed")
        self.host_subsys.wait_traffic_parallel()
