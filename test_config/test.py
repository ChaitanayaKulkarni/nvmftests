import json

def pp_json(json_thing, sort=True, indents=4):

    if type(json_thing) is str:
        return json.dumps(json.loads(json_thing),
        sort_keys=sort, indent=indents)
    else:
        return json.dumps(json_thing, sort_keys=sort, indent=indents)

class port:

    def __init__(self, port_id):
        self.port_id = port_id
        self.port = []
        self.port_dict = {}
        self.addr = {}
        self.referrals = [None]
        self.subsystems = []

    def build_addr(self):
        self.addr['adrfam'] = ""
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
        return self.port_dict

class subsystem:

    def __init__(self, nr_ns, nqn, nr_loop_dev):
        self.nr_ns = nr_ns
        self.nr_loop_dev = nr_loop_dev
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
        """
        self.allowd_hosts.append('hostnqn')
        self.attr['allow_any_host'] = '1'
        self.device['nguid'] = 'XXX'
        self.device['path'] = 'XXX'
        self.namespace['enable'] = 0
        self.namespace['nsid'] = 0
        """
        # config device
        self.device['nguid'] = ns_cfg['device']['nguid']
        self.device['path'] =  ns_cfg['device']['path']
        self.namespace['device'] = self.device
        self.namespace['enable'] = ns_cfg['enable']
        self.namespace['nsid'] = ns_cfg['nsid']
        n = self.namespace
        self.ns_list.append(n)

    def build_ns(self):
        for i in range(0, self.nr_ns):
            ns_cfg = {}
            ns_cfg['device'] = {}
            ns_cfg['device']['nguid'] = '123456'
            ns_cfg['device']['path'] = '/dev/loop' + str(i % self.nr_loop_dev)
            ns_cfg['enable'] = 0
            ns_cfg['nsid'] = i + 1
            self.add_ns(ns_cfg)

    def build_subsys(self):
        self.build_ns()
        ss_entry = {}
        ss_entry['allowed_hosts'] = self.allowd_hosts
        ss_entry['attr'] = self.attr
        ss_entry['namespaces'] = self.ns_list
        ss_entry['nqn'] = self.nqn
        ss = []
        ss.append(ss_entry)
        return ss_entry

class target_config:

    def __init__(self, config_file_path, nr_subsys, nr_ns, nr_loop_dev):

        self.ss_list = []
        self.port_list = []
        self.config_file_path = config_file_path
        self.nr_subsys = nr_subsys
        self.nr_ns = nr_ns
        self.nr_loop_dev = nr_loop_dev

    def build_target_subsys(self):

        nqn_list = []
        ss_list = []
        port_list = []
        for i in range(0, self.nr_subsys):
            nqn = "testnqn" + str(i + 1)
            subsys = subsystem(self.nr_ns, nqn, self.nr_loop_dev)
            ss_list.append(subsys.build_subsys())
            nqn_list.append(nqn)

        p = port(1)
        port_list.append(p.build_port(nqn_list))

        l = {}
        l['ports'] = port_list
        l['subsystems'] = ss_list
        data = pp_json(l)
        with open(self.config_file_path, "w+") as config_file:
            config_file.write(data)

def build_target_config(nvmf_test_config):

    with open(nvmf_test_config) as cfg_file:
        cfg = json.load(cfg_file)
        nr_loop_dev = int(cfg['nr_loop_dev'])
        nr_target_subsys = int(cfg['nr_target_subsys'])
        nr_ns_per_subsys = int(cfg['nr_ns_per_subsys'])

        t = target_config("test.json",
                          nr_target_subsys,
                          nr_ns_per_subsys,
						  nr_loop_dev)
        t.build_target_subsys()

build_target_config("../nvmftests.json")
