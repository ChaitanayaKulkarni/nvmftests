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

    def run_io_all_ns(self, iocfg):
        """ Start IOs on all the namespaces of this controller parallelly.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for host_ns in self.ns_list:
            if host_ns.start_io(iocfg) is False:
                print("start IO " + host_ns.ns_dev + " failed.")
                ret = False
                break
            print("start IO " + host_ns.ns_dev + " SUCCESS.")

        return ret

    def wait_io_all_ns(self):
        """ Wait until workqueue is empty.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        for host_ns in self.ns_list:
            host_ns.wait_io()

    def run_io_seq(self, iocfg):
        """ Issue IOs to each namespace and wait, repeat for all the
            namespaces of this controller.
            - Args :
                  - iocfg : io configuration.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for host_ns in self.ns_list:
            if host_ns.start_io(iocfg) is False:
                print("start IO " + host_ns.ns_dev + " failed.")
                ret = False
            host_ns.wait_io()
        return ret

    def run_mkfs_seq(self):
        """ Run mkfs, mount fs.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        ret = True
        for host_ns in self.ns_list:
            if host_ns.mkfs_seq() is False:
                ret = False
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

    def exec_smart_log(self, nsid="0xFFFFFFFF"):
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
        if err != 0:
            print(self.err_str + "nvme smart log failed")
            return False

        for line in proc.stdout:
            if "data_units_read" in line:
                data_units_read = \
                    string.replace(line.split(":")[1].strip(), ",", "")
            if "data_units_written" in line:
                data_units_written = \
                    string.replace(line.split(":")[1].strip(), ",", "")
            if "host_read_commands" in line:
                host_read_commands = \
                    string.replace(line.split(":")[1].strip(), ",", "")
            if "host_write_commands" in line:
                host_write_commands = \
                    string.replace(line.split(":")[1].strip(), ",", "")

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
        self.exec_smart_log()
        i = 1
        for namespace in self.ns_list:
            if self.exec_smart_log(i) is False:
                return False
            i += 1
        return True

    def validate_sysfs_host_ctrl_ns(self, ctrl):
        """ Validate sysfs entries for the host controller and namespace(s)
            - Args :
                  - ctrl : controller id.
            - Returns :
                  - True on success, False on failure.
        """
        # Validate ctrl in the sysfs
        cmd = "basename $(dirname $(grep -ls " + self.nqn + \
              " /sys/class/nvme-fabrics/ctl/*/subsysnqn))"
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE)
        for line in proc.stdout:
            line = line.strip('\n')
            if line != ctrl.split("/")[2]:
                print(self.err_str + "host ctrl " + ctrl + " not present.")
                return False
        dir_list = os.listdir("/sys/class/nvme-fabrics/ctl/" +
                              ctrl.split("/")[2] + "/")

        pat = re.compile("^" + ctrl.split("/")[2] + "+n[0-9]+$")
        for line in dir_list:
            line = line.strip('\n')
            if pat.match(line):
                if not "/dev/" + line in self.ns_dev_list:
                    print(self.err_str + "ns " + line + " not found in sysfs.")
                    return False

        print("sysfs entries for ctrl and ns created successfully.")
        return True

    def build_ctrl_ns_list(self):
        """ Generate next available controller and namespace id on the fly.
            Build the ns list for this controller.
            - Args :
                  - None.
            - Returns :
                  - ctrl and ns list on success, None on failure.
        """
        ctrl = "XXX"
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

        if ctrl == "XXX":
            print(self.err_str + "controller '/dev/nvme*' not found.")
            return None, None

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
                ns_list.append("/dev/" + line)

        if len(ns_list) == 0:
            print(self.err_str + "host ns not found for ctrl " + ctrl + ".")
            return None, None

        ctrl = "/dev/" + ctrl
        return ctrl, ns_list

    def get_value(self, k):
        """ Access nvme controller attribute's value based on the kay.
            - Args :
                  - k : represents controller's attribute.
            - Returns :
                  - value of controller's attribute.
        """
        return self.ctrl_dict[k]

    def init_ctrl_ns(self):
        """ Initialize and build namespace list and validate sysfs entries.
            - Args :
                  - None.
            - Returns :
                  - True on success, False on failure.
        """
        for ns_dev in self.ns_dev_list:
            if not stat.S_ISBLK(os.stat(ns_dev).st_mode):
                print(self.err_str + "expected block dev " + ns_dev + ".")
                return False

            print("Found NS " + ns_dev)
            host_ns = NVMeOFHostNamespace(ns_dev)
            host_ns.init()
            self.ns_list.append(host_ns)
        time.sleep(1)
        ret = self.validate_sysfs_host_ctrl_ns(self.ctrl_dev)
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
        time.sleep(1)
        self.ctrl_dev, self.ns_dev_list = self.build_ctrl_ns_list()

        if not stat.S_ISCHR(os.stat(self.ctrl_dev).st_mode):
            print(self.err_str + "failed to find char device for host ctrl.")
            return False

        ret = self.id_ctrl()
        if ret is False:
            return False

        return self.init_ctrl_ns()

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

    def del_ctrl(self):
        """ Delete subsystem and associated namespace(s).
            - Args :
                  - None.
            - Returns :
                 - True on success, False on failure.
        """
        print("Deleting subsystem " + self.nqn)
        for host_ns in self.ns_list:
            host_ns.del_ns()
        cmd = "dirname $(grep -ls " + self.nqn + \
              " /sys/class/nvme-fabrics/ctl/*/subsysnqn)"
        try:
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE)
            for line in proc.stdout:
                line = line.strip('\n')
                if not os.path.isdir(line):
                    print(self.err_str + "host ctrl dir " + self.nqn + \
                          " not present.")
                    return False
                ret = Cmd.exec_cmd("echo > " + line + "/delete_controller")
                if ret is False:
                    print(self.err_str + "failed to delete ctrl " + \
                          self.nqn + ".")
                    return False
        except Exception, err:
            print(self.err_str + str(err))
            return False

        return True
