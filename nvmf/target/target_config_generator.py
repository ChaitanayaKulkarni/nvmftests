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
""" Represents NVMe Over Fabric Target config file generator.
"""

import json


class Port:
    """
    Represents target port config generator.

        - Attributes:
            - port_id: unique port identification number.
            - port : list of the ports.
            - port_dict : dictionary to hold port attributes.
            - referrals : list of target port referals.
            - subsystems : list of the subsystems associated with this port.
    """
    def __init__(self, port_id):
        self.port_id = port_id
        self.port_dict = {}
        self.addr = {}
        self.referrals = [None]
        self.subsystems = []

    def build_addr(self):
        """ Initialize address attributes for this port.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        self.addr['adrfam'] = ""
        self.addr['traddr'] = ""
        self.addr['treq'] = "not specified"
        self.addr['trsvcid'] = ""
        self.addr['trtype'] = "loop"
        self.port_dict['addr'] = self.addr

    def build_subsystems(self, subsys_list):
        """ Initialize subsystem list associated with this port.
            - Args :
                  - None.
            -Returns :
                  - Port attributes dictionary.
        """
        self.subsystem = subsys_list
        self.port_dict['subsystems'] = self.subsystem

    def build_port(self, nqn_list):
        """ Builds port addr, subsystems, id, and referrals.
            - Args :
                  - List of the subsystem nqn associated with this port.
            - Returns :
                  - Port dictionary with valid values.
        """
        self.build_addr()
        self.build_subsystems(nqn_list)
        self.port_dict['portid'] = self.port_id
        self.port_dict['referrals'] = self.referrals
        return self.port_dict


class Subsystem:
    """
    Represents target subsystem config generator.

        - Attributes:
            - nr_ns : number of namespaces per subsystem.
            - nr_dev: number of loop devices to be used.
            - nqn : subsystem nqn.
            - ns_list : namespace list for this subsystem.
            - allowd_hosts : allowd hosts.
            - attr : subsystem attributes.
            - namespace : namespace attributes.
            - device : namespace device attibutes.
    """
    def __init__(self, nr_ns, nqn, dev_list):
        self.nr_ns = nr_ns
        self.dev_list = dev_list
        self.nqn = nqn
        self.ns_list = []
        self.allowd_hosts = []
        self.attr = {}
        self.namespace = {}
        self.device = {}
        self.nguid = "00000000-0000-0000-0000-000000000000"

    def add_ns(self, ns_cfg):
        """ Updates subsystem namespace list with new namespace.
            - Args :
                  - ns_cfg : namespace configuration.
            - Returns :
                  - None.
        """
        self.allowd_hosts = []
        self.attr = {}
        self.namespace = {}
        self.device = {}

        self.allowd_hosts.append('hostnqn')
        self.attr['allow_any_host'] = '1'
        self.device['nguid'] = ns_cfg['device']['nguid']
        self.device['path'] = ns_cfg['device']['path']
        self.namespace['device'] = self.device
        self.namespace['enable'] = ns_cfg['enable']
        self.namespace['nsid'] = ns_cfg['nsid']
        n = self.namespace
        self.ns_list.append(n)

    def build_ns(self):
        """ Build namespace configuration using available loop devices.
            - Args :
                  - ns_cfg : namespace configuration.
            - Returns :
                  - None.
        """
        for i in range(0, self.nr_ns):
            ns_cfg = {}
            ns_cfg['device'] = {}
            ns_cfg['device']['nguid'] = self.nguid
            ns_cfg['device']['path'] = self.dev_list[i % len(self.dev_list)]
            ns_cfg['enable'] = 1
            ns_cfg['nsid'] = i + 1
            self.add_ns(ns_cfg)

    def build_subsys(self):
        """ Initialize subsystem entry.
            - Args :
                  - None.
            - Returns :
                  - subsystem entry dictionary.
        """
        self.build_ns()
        ss_entry = {}
        ss_entry['allowed_hosts'] = self.allowd_hosts
        ss_entry['attr'] = self.attr
        ss_entry['namespaces'] = self.ns_list
        ss_entry['nqn'] = self.nqn
        ss = []
        ss.append(ss_entry)
        return ss_entry


class TargetConfig:
    """
    Represents target config generator.

        - Attributes:
            - ss_list : list of subsystems associsted with this target.
            - port_list : list of the ports associated with this target.
            - config_file_path : path name for generated config file.
            - nr_subsys : number of subsystems present in this target.
            - dev_list : list of devices to be used for namespaces.
    """
    def __init__(self, config_file_path, nr_subsys, nr_ns, dev_list):
        self.ss_list = []
        self.port_list = []
        self.config_file_path = config_file_path
        self.nr_subsys = nr_subsys
        self.nr_ns = nr_ns
        self.dev_list = dev_list

    def pp_json(self, json_thing, sort=True, indents=4):
        """ Prints formatted JSON output.
            - Args :
                  - json_thing : JSON string.
                  - sort : flag to sort JSON values before formatting.
                  - idents : identation width.
            -Returns :
                  - formatted JSON string.
        """
        if type(json_thing) is str:
            return json.dumps(json.loads(json_thing),
                              sort_keys=sort, indent=indents)
        return json.dumps(json_thing, sort_keys=sort, indent=indents)

    def build_target_subsys(self):
        """ Builds the Target config and dumps in JSON format.
            - Args :
                  - None.
            - Returns :
                  - None.
        """
        nqn_list = []
        ss_list = []
        port_list = []
        for i in range(0, self.nr_subsys):
            nqn = "testnqn" + str(i + 1)
            subsys = Subsystem(self.nr_ns, nqn, self.dev_list)
            ss_list.append(subsys.build_subsys())
            nqn_list.append(nqn)

        # TODO : improve support for multiple ports
        p = Port(1)
        port_list.append(p.build_port(nqn_list))

        target_config_str = {}
        target_config_str['ports'] = port_list
        target_config_str['subsystems'] = ss_list
        data = self.pp_json(target_config_str)
        with open(self.config_file_path, "w+") as config_file:
            config_file.write(data)
