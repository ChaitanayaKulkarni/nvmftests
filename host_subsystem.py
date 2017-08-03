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
from host_ns import NVMeOFHostNamespace


class NVMeOFHostController(object):
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
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def __iter__(self):
        self.ns_list_index = Const.ZERO
        return self

    def __next__(self):
        index = self.ns_list_index
        self.ns_list_index += Const.ONE
        if (len(self.ns_list) > index):
            return self.ns_list[index]
        raise StopIteration

    def next(self):
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
                    print("start IO " + ns.ns_dev + " failed.")
                    ret = False
                    break
                print("start IO " + ns.ns_dev + " SUCCESS.")
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
        """ Issue IOs to each namespace and wait, repeat for all the
            namespaces of this controller.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for ns in iter(self):
            try:
                if ns.start_io(iocfg) is False:
                    print("start IO " + ns.ns_dev + " failed.")
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

    def run_io_random(self, iocfg):
        """ Select the namespce randomely and wait for the IOs completion,
            repeat this for all the namespaces.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        num_list = range(Const.ZERO, len(self.ns_list))

        for i in range(Const.ZERO, len(self.ns_list)):
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
        # TODO : add sysfs entry check here
        return self.__ctrl_set_attr__("rescan_controller")

    def ctrl_reset(self):
        """ Issue controller reset.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        # TODO : add sysfs entry check here
        return self.__ctrl_set_attr__("reset_controller")

    def run_smart_log(self, nsid="0xFFFFFFFF"):
        """ Wrapper for nvme smart-log command.
            - Args :
                  - None.
            - Returns:
                  - True on success, False on failure.
        """
        smart_log_cmd = "nvme smart-log " + self.ctrl_dev + " -n " + str(nsid)
        print(smart_log_cmd)
        proc = subprocess.Popen(smart_log_cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        err = proc.wait()
        if err != Const.ZERO:
            print(self.err_str + "nvme smart log failed")
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

        print("data_units_read " + data_units_read)
        print("data_units_written " + data_units_written)
        print("host_read_commands " + host_read_commands)
        print("host_write_commands " + host_write_commands)
        return True

    def smart_log(self):
        """ Execute smart-log command.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        self.run_smart_log()
        i = Const.ONE
        for namespace in iter(self):
            try:
                if self.run_smart_log(i) is False:
                    return False
                i += Const.ONE
            except StopIteration:
                break
        return True

    def validate_sysfs_ns(self):
        """ Validate sysfs entries for the host controller and namespace(s)
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
                print(self.err_str + "host ctrl " + self.ctrl_dev +
                      " not present.")
                return False
        dir_list = os.listdir("/sys/class/nvme-fabrics/ctl/" + ctrl_bdev + "/")

        pat = re.compile("^" + ctrl_bdev + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                if not "/dev/" + line in self.ns_dev_list:
                    print(self.err_str + "ns " + line + " not found in sysfs.")
                    return False

        print("sysfs entries for ctrl and ns created successfully.")
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
            print(self.err_str + str(err))
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
            print(self.err_str + "controller '/dev/nvme*' not found.")
            return None, None
        # allow namespaces to appear in the /dev/
        time.sleep(2)
        # find namespace(s) associated with ctrl
        try:
            dir_list = os.listdir("/dev/")
        except Exception, err:
            print(self.err_str + str(err))
            return None, None
        pat = re.compile("^" + ctrl + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                print("Generated namespace name /dev/" + line)
                ns_list.append("/dev/" + line)

        if len(ns_list) == 0:
            print(self.err_str + "host ns not found for ctrl " + ctrl + ".")
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
        print("Expecting following namespaces " + str(self.ns_dev_list))
        for ns_dev in self.ns_dev_list:
            if not stat.S_ISBLK(os.stat(ns_dev).st_mode):
                print(self.err_str + "expected block dev " + ns_dev + ".")
                return False

            print("Found NS " + ns_dev)
            host_ns = NVMeOFHostNamespace(ns_dev)
            host_ns.init()
            self.ns_list.append(host_ns)
        # allow sysfs entries to populate
        time.sleep(1)
        ret = self.validate_sysfs_ns()
        if ret is False:
            print(self.err_str + "unable to verify sysfs entries")
            return False
        print("Host sysfs entries are validated " + str(ret))
        return ret

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
        print("CMD :- " + cmd)
        if Cmd.exec_cmd(cmd) is False:
            return False
        self.ctrl_dev, self.ns_dev_list = self.build_ns_list()

        if not stat.S_ISCHR(os.stat(self.ctrl_dev).st_mode):
            print(self.err_str + "failed to find char device for host ctrl.")
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
            print(self.err_str + "nvme id-ctrl failed")
            return False

        for line in proc.stdout:
            if line.startswith('subnqn') or \
               line.startswith('NVME Identify Controller'):
                continue
            if line.startswith('ps ') or line.strip().startswith('rwt'):
                continue
            key, val = line.split(':')
            self.ctrl_dict[key.strip()] = val.strip()

        print(self.ctrl_dict)
        print("--------------------------------------------------")
        return True

    def id_ns(self):
        """ Wrapper for executing id-ns command on all namespaces of this
            controller.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        for host_ns in self.ns_list:
            host_ns.id_ns()
            print("--------------------------------------------------")
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
        print("Deleting subsystem " + self.nqn)
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
                    print(self.err_str + "host ctrl dir " + self.nqn +
                          " not present.")
                    return False
                cmd = "nvme disconnect -n " + self.nqn
                print("disconnecting : " + cmd)
                ret = Cmd.exec_cmd(cmd)
                if ret is False:
                    print(self.err_str + "failed to delete ctrl " +
                          self.nqn + ".")
                    return False
        except Exception, err:
            print(self.err_str + str(err))
            return False

        return True
