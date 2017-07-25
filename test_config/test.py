import json

class subsystem:

	def __init__(self):
		self.ns_list = []

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

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


subsys = subsystem()

for i in range(0, 5):
	ns_cfg = {}
	ns_cfg['device'] = {}
	ns_cfg['device']['nguid'] = '123456' 
	ns_cfg['device']['path'] = '/dev/loop' + str(i)
	ns_cfg['enable'] = 0
	ns_cfg['nsid'] = i + 1
	subsys.add_ns(ns_cfg)

ss_entry = {}
ss_entry['allowd_hosts'] = subsys.allowd_hosts
ss_entry['attr'] = subsys.attr

ss_entry['namespace'] = subsys.ns_list 

ss = []
ss.append(ss_entry)

t = {}
t['subsystem'] = ss

pp_json(t) 
