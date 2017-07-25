import json

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing),
              sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


class port:
    def __init__(self, port_id):
        self.port_id = port_id
        self.port = []
        self.port_dict = {}
        self.addr = {}
        self.referrals = [None]
        self.subsystems = []

    def build_addr(self):
        self.addr['addrfam'] = ""
        self.addr['traddr'] = ""
        self.addr['treq'] = "not specified"
        self.addr['trsvcid'] = ""
        self.addr['trtype'] = "loop"
        self.port_dict['addr']  = self.addr

    def build_subsystems(self, subsys_list):
        self.subsystem = subsys_list
        self.port_dict['subsystems']  = self.subsystem

    def build_port(self, nqn_list):
        self.build_addr()
        self.build_subsystems(nqn_list)
        self.port_dict['portid'] = self.port_id
        self.port_dict['referrals'] = self.referrals
        t = {}
        l = []
        l.append(self.port_dict)
        t['ports'] = l
        return l

class subsystem:
    def __init__(self, nr_ns, nr_devices, nqn):
        self.nr_ns = nr_ns
        self.nr_devices = nr_devices
        self.nqn = nqn
        self.ns_list = []
        self.allowd_hosts = []
        self.attr = {}
        self.namespace = {}
        self.device = {}

    def add_ns(self, ns_cfg):
        self.allowd_hosts = []
        self.attr = {}
        self.namespace = {}
        self.device = {}
        self.allowd_hosts.append('hostnqn')
        self.attr['allow_any_host'] = 'XXX'
        self.device['nguid'] = 'XXX'
        self.device['path'] = 'XXX'
        self.namespace['enable'] = 0
        self.namespace['nsid'] = 0
        # config device
        self.device['nguid'] = ns_cfg['device']['nguid']
        self.device['path'] =  ns_cfg['device']['path']
        self.namespace['device'] = self.device
        self.namespace['enable'] = ns_cfg['enable']
        self.namespace['nsid'] = ns_cfg['nsid']
        n = self.namespace
        self.ns_list.append(n)

    def build_ns(self):
        for i in range(0, nr_ns):
            ns_cfg = {}
            ns_cfg['device'] = {}
            ns_cfg['device']['nguid'] = '123456'
            ns_cfg['device']['path'] = '/dev/loop' + str(i % nr_devices)
            ns_cfg['enable'] = 0
            ns_cfg['nsid'] = i + 1
            self.add_ns(ns_cfg)

    def build_subsys(self):
        self.build_ns()
        ss_entry = {}
        ss_entry['allowd_hosts'] = self.allowd_hosts
        ss_entry['attr'] = self.attr
        ss_entry['namespaces'] = self.ns_list
        ss_entry['nqn'] = self.nqn
        ss = []
        ss.append(ss_entry)
        t = {}
        t['subsystems'] = ss
        return ss

nr_ns = 2
nr_devices = 2
nqn = "testnqn1"
subsys = subsystem(nr_ns, nr_devices, nqn)
ss_list = subsys.build_subsys()

p = port(1)
port_list = p.build_port([nqn])

l = {}
l['ports'] = port_list
l['subsystems'] = ss_list

pp_json(l)
