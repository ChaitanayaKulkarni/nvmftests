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
""" Represents NVMe Over Fabric Target.
"""

import sys
import json
import subprocess
from nose.tools import assert_equal
from port import NVMeOFTargetPort

from utils.shell import Cmd
from utils.const import Const
from target_subsystem import NVMeOFTargetSubsystem


class NVMeOFTarget(object):

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
        self.cfgfs = "/sys/kernel/config/"
        self.err_str = "ERROR : " + self.__class__.__name__ + " : "

        assert_equal(self.load_configfs(), True)

    def __iter__(self):
        self.subsys_list_index = Const.ZERO
        return self

    def __next__(self):
        index = self.subsys_list_index
        self.subsys_list_index += 1
        if (len(self.subsys_list) > index):
            return self.subsys_list[index]
        raise StopIteration

    def next(self):
        return self.__next__()

    def load_configfs(self):
        """ Load configfs.
            - Args :
                  - None
            -Returns :
                  - True on success, False on failure.
        """
        ret = Cmd.exec_cmd("mountpoint -q " + self.cfgfs)
        if ret is False:
            ret = Cmd.exec_cmd("mount -t configfs none " + self.cfgfs)
            if ret is False:
                print(self.err_str + "failed to mount configfs.")
                sys.exit(ret)
            ret = Cmd.exec_cmd("mountpoint -q " + self.cfgfs)
            if ret is True:
                print("Configfs mounted at " + self.cfgfs + ".")
                ret = True
            else:
                print(self.err_str + "unable to mount configfs at " + \
                    self.cfgfs + ".")
                ret = False
        return ret

    def config_loop_target(self, config_file):
        """ Configure loop target :-
            1. Create subsystem(s) and respective namespace(s).
            2. Create port(s) and linked them to respective subsystem(s).
            3. Create in memory configuration from JSON config file.
            - Args :
                  - None
            -Returns :
                  - True on success, False on failure.
        """
        ret = Cmd.exec_cmd("modprobe nvme-loop")
        if ret is False:
            print(self.err_str + "failed to load nvme-loop.")
            return False

        try:
            config_file_handle = open(config_file, "r")
            config = json.loads(config_file_handle.read())
            config_file_handle.close()
        except Exception, err:
            print(self.err_str + str(err))
            return False

        # Subsystem
        for sscfg in config['subsystems']:
            # Create Subsystem
            subsys = NVMeOFTargetSubsystem(self.cfgfs,
                                           sscfg['nqn'],
                                           sscfg['allowed_hosts']\
                                           [Const.ALLOW_HOST_VALUE],
                                           sscfg['attr']['allow_any_host'])
            ret = subsys.init()
            if ret is False:
                # call unwind code here.
                return False

            self.subsys_list.append(subsys)

            for nscfg in sscfg['namespaces']:
                ns_attr = {}
                ns_attr['device_nguid'] = str(nscfg['device']['nguid'])
                ns_attr['device_path'] = str(nscfg['device']['path'])
                ns_attr['enable'] = str(nscfg['enable'])
                ns_attr['nsid'] = str(nscfg['nsid'])
                ret = subsys.create_ns(**ns_attr)
                if ret is False:
                    # call unwind code here.
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

            port = NVMeOFTargetPort(self.cfgfs, port_cfg['portid'], **port_cfg)
            ret = port.init()
            if ret is False:
                # call unwind code here.
                return False

            self.port_list.append(port)

            for subsys in port_cfg['subsystems']:
                ret = port.add_subsys(subsys)
                if ret is False:
                    # call unwind code here.
                    print(self.err_str + "failed to add subsystem " + \
                          subsys + " to port " + port.port_id)
                    return False

        return True

    def config(self, config_file="loop.json"):
        """ Wrapper for creating target configuration.
            - Args :
                - None
            -Returns :
                - None
        """
        ret = Cmd.exec_cmd("modprobe nvmet")
        if ret is False:
            print(self.err_str + "unable to load nvmet module.")
            return False

        ret = False
        if self.target_type == "loop":
            print("Configuring loop target")
            ret = self.config_loop_target(config_file)
        else:
            print(self.err_str + "only loop target type is supported.")

        return ret

    def delete(self):
        """ Target Cleanup.
            - Args :
                - None
            -Returns :
                - None
        """
        print("Cleanup is in progress...")

        for port in self.port_list:
            port.delete()

        for subsys in self.subsys_list:
            subsys.delete()

        print("Removing Modules :- ")
        Cmd.exec_cmd("modprobe -r nvme_loop")
        Cmd.exec_cmd("modprobe -r nvmet")
        Cmd.exec_cmd("modprobe -r nvme_fabrics")
        print("DONE.")
