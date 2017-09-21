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
""" Represents NVMe Over Fabric Target.
"""

import sys
import json
from nose.tools import assert_equal

from utils.shell import Cmd
from utils.const import Const
from utils.log import Log
from nvmf.target.target_subsystem import NVMFTargetSubsystem
from nvmf.target.port import NVMFTargetPort


class NVMFTarget(object):

    """
    Represents a target subsystem.

        - Attributes:
            - subsys_list : list of the subsystem.
            - port_list : list of the ports.
            - target_type : target type for ports.
            - cfgfs : configfs mount point.
    """
    def __init__(self, target_type):
        self.subsys_list = []
        self.port_list = []
        self.target_type = target_type
        self.cfgfs = Const.SYSFS_DEFAULT_MOUNT_PATH
        self.logger = Log.get_logger(__name__, 'target')
        self.subsys_list_index = 0

        assert_equal(self.load_configfs(), True)

    def __iter__(self):
        self.subsys_list_index = 0
        return self

    def __next__(self):
        index = self.subsys_list_index
        self.subsys_list_index += 1
        if len(self.subsys_list) > index:
            return self.subsys_list[index]
        raise StopIteration

    def next(self):
        """ Iterator next function """
        return self.__next__()

    def load_configfs(self):
        """ Load configfs.
            - Args :
                  - None
            -Returns :
                  - True on success, False on failure.
        """
        Cmd.exec_cmd("modprobe configfs")
        ret = Cmd.exec_cmd("mountpoint -q " + self.cfgfs)
        if ret is False:
            ret = Cmd.exec_cmd("mount -t configfs none " + self.cfgfs)
            if ret is False:
                self.logger.error("failed to mount configfs.")
                sys.exit(ret)
            ret = Cmd.exec_cmd("mountpoint -q " + self.cfgfs)
            if ret is True:
                self.logger.info("Configfs mounted at " + self.cfgfs + ".")
                ret = True
            else:
                self.logger.error("unable to mount configfs at " +
                                  self.cfgfs + ".")
                ret = False
        return ret

    def config_loop_target(self, config_file):
        """ Configure loop target :-
            1. Create subsystem(s) and respective namespace(s).
            2. Create port(s) and linked them to respective subsystem(s).
            3. Create in memory configuration from JSON config file.
            - Args :
                  - None.
            -Returns :
                  - True on success, False on failure.
        """
        ret = Cmd.exec_cmd("modprobe nvme-loop")
        if ret is False:
            self.logger.error("failed to load nvme-loop.")
            return False

        try:
            config_file_handle = open(config_file, "r")
            config = json.loads(config_file_handle.read())
            config_file_handle.close()
        except Exception, err:
            self.logger.error(str(err) + ".")
            return False

        # Subsystem
        for sscfg in config['subsystems']:
            # Create Subsystem
            subsys = NVMFTargetSubsystem(self.cfgfs,
                                         sscfg['nqn'],
                                         sscfg['allowed_hosts']
                                         [Const.ALLOW_HOST_VALUE],
                                         sscfg['attr']['allow_any_host'])
            if subsys.init() is False:
                return False

            self.subsys_list.append(subsys)

            for nscfg in sscfg['namespaces']:
                ns_attr = {}
                ns_attr['device_nguid'] = str(nscfg['device']['nguid'])
                ns_attr['device_path'] = str(nscfg['device']['path'])
                ns_attr['enable'] = str(nscfg['enable'])
                ns_attr['nsid'] = str(nscfg['nsid'])
                if subsys.create_ns(**ns_attr) is False:
                    return False

        # Port
        for pcfg in config['ports']:
            port_cfg = {}
            port_cfg['addr_treq'] = pcfg['addr']['treq']
            port_cfg['addr_traddr'] = pcfg['addr']['traddr']
            port_cfg['addr_trtype'] = pcfg['addr']['trtype']
            port_cfg['addr_adrfam'] = pcfg['addr']['adrfam']
            port_cfg['addr_trsvcid'] = pcfg['addr']['trsvcid']
            port_cfg['portid'] = str(pcfg['portid'])
            port_cfg['subsystems'] = pcfg['subsystems']

            port = NVMFTargetPort(self.cfgfs, port_cfg['portid'], **port_cfg)
            if port.init() is False:
                return False

            self.port_list.append(port)

            for subsys in port_cfg['subsystems']:
                ret = port.add_subsys(subsys)
                if ret is False:
                    self.logger.error("failed to add subsystem " +
                                      subsys + " to port " +
                                      port.port_id + ".")
                    return False

        return True

    def config(self, config_file="config/loop.json"):
        """ Wrapper for creating target configuration.
            - Args :
                  - None.
            -Returns :
                  - None.
        """
        if Cmd.exec_cmd("modprobe nvme") is False:
            self.logger.error("failed to load nvme.")
            return False

        if Cmd.exec_cmd("modprobe nvmet") is False:
            self.logger.error("unable to load nvmet module.")
            return False

        ret = False
        if self.target_type == "loop":
            self.logger.info("Configuring loop target ... ")
            ret = self.config_loop_target(config_file)
        else:
            self.logger.error("only loop target type is supported.")

        return ret

    def delete(self):
        """ Target Cleanup.
            - Args :
                  - None.
            -Returns :
                  - True on success, False on failure.
        """
        self.logger.info("Cleanup is in progress ...")
        ret = True
        for port in self.port_list:
            if port.delete() is False:
                ret = False

        for subsys in iter(self):
            if subsys.delete() is False:
                ret = False

        self.logger.info("Removing Modules ...")
        Cmd.exec_cmd("modprobe -r nvme_loop")
        Cmd.exec_cmd("modprobe -r nvmet")
        Cmd.exec_cmd("modprobe -r nvme_fabrics")
        self.logger.info("DONE.")
        return ret
