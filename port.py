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
""" Represents NVMe Over Fabric Target Port.
"""

import os
import shutil

from utils.shell import Cmd
from utils.const import Const


class NVMFTargetPort(object):
    """
    Represents a target port.

        - Attributes :
            - cfgfs : configfs mountpoint.
            - port_id : port identification number.
            - port_conf : dictionary to hold the port attributes.
    """
    def __init__(self, cfgfs, port_id, **port_conf):
        """ Constructor for NVMFTargetPort.
            - Args :
                  - cfgfs : configfs path.
                  - port_id : port identifier.
                  - port_conf : port configuration list.
        """
        self.cfgfs = cfgfs
        self.port_id = port_id
        self.port_conf = {}
        self.port_path = self.cfgfs + "/nvmet/ports/" + port_id + "/"
        self.port_conf['addr_treq'] = port_conf['addr_treq']
        self.port_conf['addr_traddr'] = port_conf['addr_traddr']
        self.port_conf['addr_trtype'] = port_conf['addr_trtype']
        self.port_conf['addr_adrfam'] = port_conf['addr_adrfam']
        self.port_conf['addr_trsvcid'] = port_conf['addr_trsvcid']
        self.port_conf['referrals'] = Const.XXX
        self.port_conf['subsystems'] = port_conf['subsystems']
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

    def init(self):
        """ Create and initialize port.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        if self.port_conf['addr_trtype'] != "loop":
            print(self.err_str + "only loop transport type is supported.")
            return False

        ret = Cmd.exec_cmd("mkdir -p " + self.port_path)
        if ret is False:
            print(self.err_str + "failed to create " + self.port_path + ".")
            return False

        # initialize transport type
        print("Port " + self.port_path + " created successfully.")

        ret = Cmd.exec_cmd("echo -n \"" + self.port_conf['addr_trtype'] +
                           "\" > " + self.port_path + "/addr_trtype")
        status = "Port " + self.port_path + " initialized successfully."
        if ret is False:
            status = self.err_str + "trtype " + self.port_path + " failed."

        print(status)
        return ret

    def add_subsys(self, subsys_name):
        """ Link Subsystem to this port.
            - Args :
                 - subsys_name : subsstem nqn to be linked
            - Returns :
                  - True on success, False on failure.
        """
        src = self.cfgfs + "/nvmet/subsystems/" + subsys_name
        if not os.path.exists(src):
            print(self.err_str + "subsystem '" + src + "' not present.")
            return False
        dest = self.port_path + "/subsystems/"
        cmd = "ln -s " + src + " " + dest
        print(cmd)
        ret = Cmd.exec_cmd("ln -s " + src + " " + dest)
        return ret

    def delete(self):
        """ Delete this port.
            - Args :
                - None
            -Returns :
                  - True on success, False on failure.
        """
        print("Deleting port " + self.port_id)
        subsys_symlink = self.port_path + "/subsystem/"
        try:

            if os.path.isdir(subsys_symlink):
                shutil.rmtree(subsys_symlink, ignore_errors=True)
                print("Unlink subsystem fromn port successfully.")

            if os.path.isdir(self.port_path):
                shutil.rmtree(self.port_path, ignore_errors=True)

        except Exception, err:
            print(self.err_str + str(err) + ".")
            return False

        print("Removed port " + self.port_path + " successfully.")
        return True
