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
""" Represents NVMe Over Fabric Target Subsystem.
"""

import os
import shutil

from utils.shell import Cmd
from utils.const import Const
from utils.log import Log
from nvmf.target.target_ns import NVMFTargetNamespace


class NVMFTargetSubsystem(object):
    """
    Represents a target subsystem.

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
        self.subsys_path = self.cfgfs + Const.SYSFS_NVMET_SUBSYS + nqn + "/"
        self.allowed_hosts = allowed_hosts
        self.attr_allow_any_host = attr_allow_any_host
        self.logger = Log.get_logger(__name__, 'target_subsystem')
        self.ns_list_index = 0

    def __iter__(self):
        self.ns_list_index = 0
        return self

    def __next__(self):
        index = self.ns_list_index
        self.ns_list_index += 1
        if len(self.ns_list) > index:
            return self.ns_list[index]
        raise StopIteration

    def next(self):
        """ Iterator next function """
        return self.__next__()

    def init(self):
        """ Create and initialize target subsystem.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        # create subsystem dir
        self.logger.info("Creating subsys path " + self.subsys_path + ".")
        try:
            os.makedirs(self.subsys_path)
        except Exception, err:
            self.logger.error(str(err) + ".")
            return False
        # allow any host
        self.logger.info("Configuring allowed hosts ...")
        ret = Cmd.exec_cmd("echo " + self.attr_allow_any_host + " >" +
                           self.subsys_path + "/attr_allow_any_host")
        if ret is False:
            self.logger.error(self.subsys_path + " creation failed.")
        else:
            self.logger.info(self.subsys_path + " created successfully.")
        return ret

    def create_ns(self, **ns_attr):
        """ Create, initialize and store namespace in subsystem's list.
            - Args :
                - ns_attr : namespace attributes.
            - Returns :
                - namespace handle on success, None on error.
        """
        ns_id = len(self.ns_list) + 1

        ns = NVMFTargetNamespace(self.cfgfs, self.nqn, ns_id, **ns_attr)
        if ns.init() is False:
            return None
        self.ns_list.append(ns)
        return ns

    def delete_ns(self, ns):
        """ Delete single namespace.
            - Args :
                - ns : target namespace object to be deleted.
            - Returns :
                - True on success, False on failure.
        """
        self.logger.info("Deleting namespace " + self.nqn + " : " +
                         ns.ns_path + ".")
        ret = ns.delete()
        if ret is False:
            self.logger.error("delete ns failed for " + ns.ns_path + ".")

        return ret

    def delete(self):
        """ Delete subsystem and associated namespace(s).
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        self.logger.info("Deleting subsystem " + self.nqn)
        ret = True
        for ns in iter(self):
            if self.delete_ns(ns) is False:
                # try and continue deleting namespaces for cleanup after error
                ret = False

        if os.path.exists(self.subsys_path):
            shutil.rmtree(self.subsys_path, ignore_errors=True)

        return ret
