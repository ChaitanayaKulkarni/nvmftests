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
NVMF test parallel IOs on all controllers :-

    1. From the config file create Target.
    2. From the config file create host and connect to target.
    3. Run parallel IOs on all available controller(s) and its nvmespace(s).
    4. Delete Host.
    5. Delete Target.
"""


from nose.tools import assert_equal
from nvmf.misc.null_blk import NullBlk
from nvmf_test import NVMFTest


class TestNVMFParallelFabric(NVMFTest):

    """ Represents Parallel Subsystem IO testcase """

    def __init__(self):
        NVMFTest.__init__(self)
        self.setup_log_dir(self.__class__.__name__)

    def setUp(self):
        """ Pre section of testcase """
        self.null_blk = NullBlk(self.data_size, self.block_size, self.nr_dev)
        self.null_blk.init()
        self.build_target_config(self.null_blk.dev_list)
        super(TestNVMFParallelFabric, self).common_setup()

    def tearDown(self):
        """ Post section of testcase """
        super(TestNVMFParallelFabric, self).common_tear_down()
        self.null_blk.delete()

    def test_parallel_io(self):
        """ Testcase main """
        print("Now Running " + self.__class__.__name__)
        ret = self.host_subsys.run_perf_parallel(self.fio_read)
        assert_equal(ret, True, "ERROR : running IOs failed.")
