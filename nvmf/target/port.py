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
""" Represents NVMe Over Fabric Target Port.
"""

import os
import shutil
import logging

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
        self.logger = logging.getLogger(__name__)
        self.log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        self.log_format += '%(filename)20s %(funcName)20s %(lineno)4d'
        self.log_format += '%(pathname)s'
        self.formatter = logging.Formatter(self.log_format)
        self.logger.setLevel(logging.WARNING)

    def init(self):
        """ Create and initialize port.
            - Args :
                - None.
            - Returns :
                - True on success, False on failure.
        """
        if self.port_conf['addr_trtype'] != "loop":
            self.logger.error("only loop transport type is supported.")
            return False

        ret = Cmd.exec_cmd("mkdir -p " + self.port_path)
        if ret is False:
            self.logger.error("failed to create " + self.port_path + ".")
            return False

        # initialize transport type
        self.logger.info("Port " + self.port_path + " created successfully.")

        ret = Cmd.exec_cmd("echo -n \"" + self.port_conf['addr_trtype'] +
                           "\" > " + self.port_path + "/addr_trtype")
        status = "Port " + self.port_path + " initialized successfully."
        if ret is False:
            status = self.err_str + "trtype " + self.port_path + " failed."

        self.logger.info(status)
        return ret

    def add_subsys(self, subsys_name):
        """ Link Subsystem to this port.
            - Args :
                  - subsys_name : subsystem nqn to be linked.
            - Returns :
                  - True on success, False on failure.
        """
        src = self.cfgfs + "/nvmet/subsystems/" + subsys_name
        if not os.path.exists(src):
            self.logger.error("subsystem '" + src + "' not present.")
            return False
        dest = self.port_path + "/subsystems/"
        cmd = "ln -s " + src + " " + dest
        self.logger.info(cmd)
        ret = Cmd.exec_cmd("ln -s " + src + " " + dest)
        return ret

    def delete(self):
        """ Delete this port.
            - Args :
                  - None.
            -Returns :
                  - True on success, False on failure.
        """
        self.logger.info("Deleting port " + self.port_id + ".")
        subsys_symlink = self.port_path + "/subsystem/"
        try:

            if os.path.isdir(subsys_symlink):
                shutil.rmtree(subsys_symlink, ignore_errors=True)
                self.logger.info("Unlink subsystem fromn port successfully.")

            if os.path.isdir(self.port_path):
                shutil.rmtree(self.port_path, ignore_errors=True)

        except Exception, err:
            self.logger.error(str(err) + ".")
            return False

        self.logger.info("Removed port " + self.port_path + " successfully.")
        return True
