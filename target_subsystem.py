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
""" Represents NVMe Over Fabric Target Subsystem.
"""

import os
import shutil
import subprocess

from utils.shell import Cmd
from target_ns import NVMeOFTargetNamespace


class NVMeOFTargetSubsystem(object):
    """
    Represents a target controller.

        - Attributes :
            - ns_list : list of namespaces.
            - cfgfs : configfs path.
            - nqn : subsystem nqn.
            - subsys_path : subsystem path in configfs.
            - allowed_hosts : configfs allowed host attribute.
            - attr_allow_any_host : configfs allow any host attribute.
    """
    def __init__(self, cfgfs, nqn, allowed_hosts, attr_allow_any_host):
        self.ns_list = []
        self.cfgfs = cfgfs
        self.nqn = nqn
        self.subsys_path = self.cfgfs + "/nvmet/subsystems/" + nqn + "/"
        self.allowed_hosts = allowed_hosts
        self.attr_allow_any_host = attr_allow_any_host
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def init_subsys(self):
        """ create and initialize subsystem.
            - Args :
                - None.
            - Returns :
                  - True on success, False on failure.
        """
        print("Loading nvme-loop module ...")
        ret = Cmd.exec_cmd("modprobe nvme-loop")
        if ret is False:
            print(self.err_str + "unable to load nvme-loop module.")
            return False
        # create subsystem dir
        print("Creating subsys path " + self.subsys_path + ".")
        try:
            os.makedirs(self.subsys_path)
        except Exception, err:
            print(self.err_str + str(err))
            return False
        # allow any host
        print("Configuring allowed hosts ...")
        ret = Cmd.exec_cmd("echo " + self.attr_allow_any_host + " >" +
                            self.subsys_path + "/attr_allow_any_host")
        status = "Target Subsys " + self.subsys_path + " created successfully."
        if ret is False:
            status = self.err_str + "create " + self.subsys_path + " failed."
        print(status)

        return ret

    def create_ns(self, **ns_attr):
        """ Create, initialize and store namespace in subsystem's list.
            - Args :
                - ns_attr : namespace attributes.
            - Returns :
                - namespace handle on success, None on error.
        """
        ns_id = self.generate_next_ns_id()

        ns = NVMeOFTargetNamespace(self.cfgfs, self.nqn, ns_id, **ns_attr)
        if ns.init_ns() is False:
            return None
        self.ns_list.append(ns)
        return ns

    def del_ns(self, ns):
        """ Delete single namespace.
            - Args :
                - None.
            - Returns :
                - None.
        """
        print("Deleting namespace " + self.nqn + " : " + ns.ns_path)

        ret = ns.del_ns()
        if ret is False:
            print("ERROR : delete ns failed for " + ns.ns_path + ".")

        return ret

    def del_subsys(self):
        """ Delete subsystem and associated namespace(s).
            - Args :
                - None.
            - Returns :
                - None.
        """
        print("Deleting subsystem " + self.nqn)
        for ns in self.ns_list:
            self.del_ns(ns)

        if os.path.exists(self.subsys_path):
            shutil.rmtree(self.subsys_path, ignore_errors=True)

    def generate_next_ns_id(self):
        """ Return next namespace id.
            - Args :
                - None.
            - Returns :
                - next namespace id.
        """
        return len(self.ns_list) + 1
