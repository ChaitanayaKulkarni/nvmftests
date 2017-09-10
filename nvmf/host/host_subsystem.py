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
""" Represents NVMe Over Fabric Host Controller.
"""

import re
import os
import stat
import time
import random
import string
import subprocess
from natsort import natsorted

from utils.const import Const
from utils.shell import Cmd
from utils.log import Log
from nvmf.host.host_ns import NVMFHostNamespace


class NVMFHostController(object):
    """
    Represents a host controller.

        - Attributes :
            - nqn : ctrltem nqn.
            - ctrl_dev : controller device.
            - ctrl_dict : controller attributes.
            - ns_list : list of namespaces.
            - ns_dev_list : namespace device list.
            - transport : transport type.
    """
    def __init__(self, nqn, transport):
        self.nqn = nqn
        self.ctrl_dev = None
        self.ctrl_dict = {}
        self.ns_list = []
        self.ns_dev_list = []
        self.transport = transport
        self.ns_list_index = 0
        self.logger = Log.get_logger(__name__, 'host_subsystem')

    def __iter__(self):
        self.ns_list_index = 0
        return self

    def __next__(self):
        index = self.ns_list_index
        self.ns_list_index += 1
        if (len(self.ns_list) > index):
            return self.ns_list[index]
        raise StopIteration

    def next(self):
        """ Iterator next function """
        return self.__next__()

    def run_io_all_ns(self, iocfg):
        """ Start IOs on all the namespaces of this controller parallelly.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ns in iter(self):
            try:
                if ns.start_io(iocfg) is False:
                    self.logger.error("start IO " + ns.ns_dev + ".")
                    ret = False
                    break
                self.logger.info("start IO " + ns.ns_dev + " SUCCESS.")
            except StopIteration:
                break

        return ret

    def wait_io_all_ns(self):
        """ Wait until workqueue is empty.
            - Args :
                  - None.
            - Returns :
                  - True if namespace wait IO is successful, False otherwise.
        """
        for ns in iter(self):
            try:
                ret = ns.wait_io()
                if ret is False:
                    return False
            except StopIteration:
                break
        return True

    def run_io_seq(self, iocfg):
        """ Exercie IOs on each namespace.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ns in iter(self):
            try:
                if ns.start_io(iocfg) is False:
                    self.logger.error("start IO " + ns.ns_dev + ".")
                    ret = False
                    break
                ret = ns.wait_io()
            except StopIteration:
                break
        return ret

    def run_mkfs_seq(self, fs_type):
        """ Run mkfs, mount fs.
            - Args :
                  - fs_type : file system type.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ns in iter(self):
            try:
                if ns.mkfs(fs_type) is False:
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
        for ns in iter(self):
            try:
                if ns.run_fs_ios(iocfg) is False:
                    ret = False
                    break
            except StopIteration:
                break
        return ret

    def run_io_random(self, iocfg):
        """ Select the namespce randomely and wait for the IOs completion,
            repeat this for all the namespaces.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        num_list = range(0, len(self.ns_list))

        for i in range(0, len(self.ns_list)):
            random.shuffle(num_list)
            ns_id = num_list.pop()

            host_ns = self.ns_list[ns_id]
            if host_ns.start_io(iocfg) is False:
                return False
            host_ns.wait_io()

        return True

    def __ctrl_set_attr__(self, attr):
        """ Set host controller attribute.
            - Args :
                  - attr : sysfs attribute to set.
            - Returns :
                  - True on success, False on failure.
        """
        sysfs_path = "/sys/class/nvme-fabrics/ctl/"
        cmd = "echo 1 >" + sysfs_path + self.ctrl_dev.split('/')[-1] \
              + "/" + attr
        return Cmd.exec_cmd(cmd)

    def ctrl_rescan(self):
        """ Issue controller rescan.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        return self.__ctrl_set_attr__("rescan_controller")

    def ctrl_reset(self):
        """ Issue controller reset.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        return self.__ctrl_set_attr__("reset_controller")

    def run_smart_log(self, nsid="0xFFFFFFFF"):
        """ Wrapper for nvme smart-log command.
            - Args :
                  - None.
            - Returns:
                  - True on success, False on failure.
        """
        smart_log_cmd = "nvme smart-log " + self.ctrl_dev + " -n " + str(nsid)
        self.logger.info(smart_log_cmd)
        proc = subprocess.Popen(smart_log_cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        err = proc.wait()
        if err != 0:
            self.logger.error("nvme smart log failed.")
            return False

        for line in proc.stdout:
            if "data_units_read" in line:
                temp_str = line.split(":")[Const.SMART_LOG_VALUE].strip()
                data_units_read = string.replace(temp_str, ",", "")
            if "data_units_written" in line:
                temp_str = line.split(":")[Const.SMART_LOG_VALUE].strip()
                data_units_written = string.replace(temp_str, ",", "")
            if "host_read_commands" in line:
                temp_str = line.split(":")[Const.SMART_LOG_VALUE].strip()
                host_read_commands = string.replace(temp_str, ",", "")
            if "host_write_commands" in line:
                temp_str = line.split(":")[Const.SMART_LOG_VALUE].strip()
                host_write_commands = string.replace(temp_str, ",", "")

        self.logger.info("data_units_read " + data_units_read)
        self.logger.info("data_units_written " + data_units_written)
        self.logger.info("host_read_commands " + host_read_commands)
        self.logger.info("host_write_commands " + host_write_commands)
        return True

    def smart_log(self):
        """ Execute smart-log command.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        self.run_smart_log()
        i = 1
        for ns in iter(self):
            try:
                if self.run_smart_log(i) is False:
                    return False
                i += 1
            except StopIteration:
                break
        return True

    def validate_sysfs_ns(self):
        """ Validate sysfs entries for the host controller and namespace(s).
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ctrl_bdev = self.ctrl_dev.split("/")[Const.CTRL_BLK_FILE_NAME]
        # Validate ctrl in the sysfs
        cmd = "basename $(dirname $(grep -ls " + self.nqn + \
              " /sys/class/nvme-fabrics/ctl/*/subsysnqn))"
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        for line in proc.stdout:
            line = line.strip('\n')
            # compare nvmeN in /dev/nvmeN in sysfs
            if line != ctrl_bdev:
                self.logger.error("host ctrl " + self.ctrl_dev +
                                  " not present.")
                return False
        dir_list = os.listdir("/sys/class/nvme-fabrics/ctl/" + ctrl_bdev + "/")

        pat = re.compile("^" + ctrl_bdev + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                if "/dev/" + line not in self.ns_dev_list:
                    self.logger.error("ns " + line + " not found in sysfs.")
                    return False

        self.logger.info("sysfs entries for ctrl and ns created successfully.")
        return True

    def build_ns_list(self):
        """ Generate next available controller and namespace id on the fly.
            Build the ns list for this controller.
            - Args :
                  - None.
            - Returns :
                  - ctrl and ns list on success, None on failure.
        """
        ctrl = Const.XXX
        ns_list = []
        try:
            dev_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err) + ".")
            return None, None
        dev_list = natsorted(dev_list, key=lambda y: y.lower())
        # we assume that atleast one namespace is created on target
        # find ctrl
        pat = re.compile("^nvme[0-9]+$")
        for line in dev_list:
            line = line.strip('\n')
            if pat.match(line):
                ctrl = line

        if ctrl == Const.XXX:
            self.logger.error("controller '/dev/nvme*' not found.")
            return None, None
        # allow namespaces to appear in the /dev/
        time.sleep(2)
        # find namespace(s) associated with ctrl
        try:
            dir_list = os.listdir("/dev/")
        except Exception, err:
            self.logger.error(str(err))
            return None, None
        pat = re.compile("^" + ctrl + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                self.logger.info("Generated namespace name /dev/" + line + ".")
                ns_list.append("/dev/" + line)

        if len(ns_list) == 0:
            self.logger.error("host ns not found for ctrl " + ctrl + ".")
            return None, None

        ctrl = "/dev/" + ctrl
        return ctrl, ns_list

    def init_ns(self):
        """ Initialize and build namespace list and validate sysfs entries.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        self.logger.info("Expecting following namespaces " +
                         str(self.ns_dev_list) + ".")
        for ns_dev in self.ns_dev_list:
            if not stat.S_ISBLK(os.stat(ns_dev).st_mode):
                self.logger.error("expected block dev " + ns_dev + ".")
                return False

            self.logger.info("Found NS " + ns_dev + ".")
            host_ns = NVMFHostNamespace(ns_dev)
            host_ns.init()
            self.ns_list.append(host_ns)
        # allow sysfs entries to populate
        time.sleep(1)
        ret = self.validate_sysfs_ns()
        if ret is False:
            self.logger.error("unable to verify sysfs entries.")
            return False
        self.logger.info("Host sysfs entries are validated " + str(ret) + ".")
        return ret

    def validate_fabric_ctrl(self):
        if not stat.S_ISCHR(os.stat(self.ctrl_dev).st_mode):
            self.logger.error("failed to find char device for host ctrl.")

        cmd = "find /sys/devices -name " + self.ctrl_dev.split("/")[-2] \
              + " | grep nvme-fabric"
        print cmd
        return Cmd.exec_cmd(cmd)

    def init_ctrl(self):
        """ Initialize controller and build controller attributes.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        # initialize nqn and transport
        cmd = "echo  \"transport=" + self.transport + ",nqn=" + \
              self.nqn + "\" > /dev/nvme-fabrics"
        self.logger.info("Host Connect command : " + cmd)
        if Cmd.exec_cmd(cmd) is False:
            self.logger.info("ERROR : host connect command failed")
            return False
        self.ctrl_dev, self.ns_dev_list = self.build_ns_list()

        if self.validate_fabric_ctrl() is False:
            return False

        ret = self.id_ctrl()
        if ret is False:
            return False

        return self.init_ns()

    def id_ctrl(self):
        """ Wrapper for executing id-ctrl command.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        id_ctrl_cmd = "nvme id-ctrl " + self.ctrl_dev
        proc = subprocess.Popen(id_ctrl_cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        err = proc.wait()
        if err != 0:
            self.logger.error("nvme id-ctrl failed.")
            return False

        for line in proc.stdout:
            if line.startswith('subnqn') or \
               line.startswith('NVME Identify Controller'):
                continue
            if line.startswith('ps ') or line.strip().startswith('rwt'):
                continue
            key, val = line.split(':')
            self.ctrl_dict[key.strip()] = val.strip()

        self.logger.info(self.ctrl_dict)
        return True

    def id_ns(self):
        """ Wrapper for executing id-ns command on all namespaces of this
            controller.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        for host_ns in iter(self):
            if host_ns.id_ns() is False:
                return False
        return True

    def ns_descs(self):
        """ Wrapper for executing ns_descs command on all namespaces of this
            controller.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        for host_ns in iter(self):
            if host_ns.ns_descs() is False:
                return False
        return True

    def generate_next_ns_id(self):
        """ Return next namespace id.
            - Args :
                  - None.
            - Returns :
                  - next namespace id.
        """
        return len(self.ns_list) + 1

    def delete(self):
        """ Delete subsystem and associated namespace(s).
            - Args :
                  - None.
            - Returns :
                 - True on success, False on failure.
        """
        self.logger.info("Deleting subsystem " + self.nqn + ".")
        for host_ns in self.ns_list:
            host_ns.delete()
        cmd = "dirname $(grep -ls " + self.nqn + \
              " /sys/class/nvme-fabrics/ctl/*/subsysnqn)"
        try:
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE)
            for line in proc.stdout:
                line = line.strip('\n')
                if not os.path.isdir(line):
                    self.logger.error("host ctrl dir " + self.nqn +
                                      " not present.")
                    return False
                cmd = "nvme disconnect -n " + self.nqn
                self.logger.info("disconnecting : " + cmd)
                ret = Cmd.exec_cmd(cmd)
                if ret is False:
                    self.logger.error("failed to delete ctrl " +
                                      self.nqn + ".")
                    return False
        except Exception, err:
            self.logger.error(str(err) + ".")
            return False

        return True
