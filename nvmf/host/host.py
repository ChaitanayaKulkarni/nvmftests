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
""" Represents NVMe Over Fabric Host Subsystem.
"""

import json
import random
from nose.tools import assert_equal

from utils.shell import Cmd
from utils.log import Log
from nvmf.host.host_subsystem import NVMFHostController


class NVMFHost(object):

    """
    Represents a host.

        - Attributes :
              - target_type : rdma/loop/fc. (only loop supported now)
              - ctrl_list : list of the host controllers.
    """
    def __init__(self, target_type):
        self.target_type = target_type
        self.ctrl_list = []
        self.ctrl_list_index = 0
        self.logger = Log.get_logger(__name__, 'host')
        assert_equal(self.load_modules(), True)

    def __iter__(self):
        self.ctrl_list_index = 0
        return self

    def __next__(self):
        index = self.ctrl_list_index
        self.ctrl_list_index += 1
        if len(self.ctrl_list) > index:
            return self.ctrl_list[index]
        raise StopIteration

    def next(self):
        """ Iterator next function """
        return self.__next__()

    def load_modules(self):
        """ Wrapper for Loading NVMF Host modules.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        if Cmd.exec_cmd("modprobe nvme-fabrics") is False:
            self.logger.error("unable to load nvme-fabrics.")
            return False
        return True

    def config_loop(self, config_file):
        """ Configure host for loop target :-
            1. Load config from json file.
            2. Create Controller list.
            - Args :
                - config_file : json config file.
            -Returns :
                - True on success, False on failure.
        """
        try:
            config_file_handle = open(config_file, "r")
            config = json.loads(config_file_handle.read())
            config_file_handle.close()
        except Exception, err:
            self.logger.error(str(err) + ".")
            return False

        for sscfg in config['subsystems']:
            ctrl = NVMFHostController(sscfg['nqn'], "loop")
            if ctrl.init_ctrl()is False:
                self.logger.error("ctrl init " + str(ctrl.ctrl_dev) + ".")
                return False
            self.ctrl_list.append(ctrl)
        return True

    def run_traffic_parallel(self, iocfg):
        """ Run parallel IO traffic on all host controller(s) and
            wait for completion.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - None.
        """
        ret = True
        self.logger.info("Starting traffic parallelly on all controllers ...")
        for ctrl in iter(self):
            if ctrl.run_io_all_ns(iocfg) is False:
                ret = False
        return ret

    def wait_traffic_parallel(self):
        """ Wait for IOs completion on all controllers.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - None.
        """
        ret = True
        self.logger.info("Waiting for all threads to finish the IOs ...")
        for ctrl in iter(self):
            if ctrl.wait_io_all_ns() is False:
                self.logger.error("wait on " + ctrl.ctrl_dev + ".")
                ret = False

        return ret

    def run_ios_parallel(self, iocfg):
        """ Run parallel IOs on all host controller(s) and
            wait for completion.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - None.
        """
        if self.run_traffic_parallel(iocfg) is False:
            return False

        if self.wait_traffic_parallel() is False:
            return False

        return True

    def run_perf_parallel(self, iocfg):
        """ Run parallel IO traffic on all host controller(s) and
            wait for completion.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - None.
        """
        if self.run_ios_parallel(iocfg) is False:
            return False

        # add perf report generation mechanism here

        return True

    def run_ios_seq(self, iocfg):
        """ Run IOs on all host controllers sequentially.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - True on success, False on failure.
        """
        self.logger.info("Starting IOs seq ...")
        ret = True
        for ctrl in iter(self):
            try:
                if ctrl.run_io_seq(iocfg) is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def run_ios_random(self, iocfg):
        """ Select a controller from the list of controllers
            randomly and run IOs. Exhaust entire list.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - None.
        """
        ctrl_list = range(0, len(self.ctrl_list))

        ret = True
        for i in range(0, len(self.ctrl_list)):
            random.shuffle(ctrl_list)
            ctrl_id = ctrl_list.pop()
            ctrl = self.ctrl_list[ctrl_id]
            if ctrl.run_io_random(iocfg) is False:
                ret = False
                break
        return ret

    def ctrl_rescan(self):
        """ Run controller_rescan on all host controllers sequentially.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            try:
                if ctrl.ctrl_rescan() is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def ctrl_reset(self):
        """ Run controller_reset on all host controllers sequentially.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            try:
                if ctrl.ctrl_reset() is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def smart_log(self):
        """ Execute smart log.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            if ctrl.smart_log() is False:
                ret = False
                break
        return ret

    def id_ctrl(self):
        """ Execute id-ctrl on all the controllers(s).
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            if ctrl.id_ctrl() is False:
                ret = False
                break
        return ret

    def id_ns(self):
        """ Execute id-ns on controller(s) and all its namespace(s).
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            if ctrl.id_ns() is False:
                ret = False
                break
        return ret

    def ns_descs(self):
        """ Execute ns-descs on all namespace(s).
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            if ctrl.ns_descs() is False:
                ret = False
                break
        return ret

    def get_ns_id(self):
        """ Execute get-ns-id on all namespace(s).
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            if ctrl.get_ns_id() is False:
                ret = False
                break
        return ret

    def mkfs_seq(self, fs_type):
        """ Run mkfs, mount fs and run IOs.
            - Args :
                - fs_type : file system type.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            try:
                if ctrl.run_mkfs_seq(fs_type) is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def run_fs_ios(self, iocfg):
        """ Run IOs on mounted file system.
            - Args :
                - iocfg : io configuration.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for ctrl in iter(self):
            try:
                if ctrl.run_fs_ios(iocfg) is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def config(self, config_file="config/loop.json"):
        """ Configure Host based on the target transport.
            - Args :
                - config_file : JSON config.
            - Returns :
                - True on success, False on failure.
        """
        ret = False
        if self.target_type == "loop":
            self.logger.info("Configuring loop host")
            ret = self.config_loop(config_file)
            self.logger.info("Host configure successfully")
        else:
            self.logger.error("only loop target type is supported.")
        return ret

    def delete(self):
        """ Delete all the Host Controllers.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        ret = True
        for subsys in iter(self):
            if subsys.delete() is False:
                ret = False
        return ret
