from transitions.extensions import MachineFactory


class target(object):
    """ """
    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('state1.png', prog='dot')


GM = MachineFactory.get_predefined(graph=True, nested=True, locked=True)

target_ns_cfg_states = {'name': 'subsys_cfg',
                        'children': ['ns_start',
                                     'ns_init',
                                     'ns_cfg',
                                     'ns_online',
                                     'ns_offline',
                                     'ns_dead']}
target_subsys_cfg_states = {'name': 'cfg',
                            'children': ['subsys_start',
                                         'subsys_init',
                                         target_ns_cfg_states,
                                         'subsys_online',
                                         'subsys_offline',
                                         'subsys_dead']}

states = ['start', 'init', target_subsys_cfg_states,
          'online', 'offline', 'dead']
transitions = [
    ['nsinit', 'cfg_subsys_cfg_ns_start', 'cfg_subsys_cfg_ns_init'],
    ['nscfg', 'cfg_subsys_cfg_ns_init', 'cfg_subsys_cfg_ns_cfg'],
    ['nsonline', 'cfg_subsys_cfg_ns_cfg', 'cfg_subsys_cfg_ns_online'],
    ['nsoffline', 'cfg_subsys_cfg_ns_online', 'cfg_subsys_cfg_ns_offline'],
    ['nsdead', 'cfg_subsys_cfg_ns_offline', 'cfg_subsys_cfg_ns_dead'],
    ['subsysnsinit', 'cfg_subsys_start', 'cfg_subsys_init'],
    ['subsysinit', 'cfg_subsys_start', 'cfg_subsys_init'],
    ['subsyscfg', 'cfg_subsys_init', 'cfg_subsys_cfg'],
    ['subsysonline', 'cfg_subsys_cfg', 'cfg_subsys_online'],
    ['subsysoffline', 'cfg_subsys_online', 'cfg_subsys_offline'],
    ['subsysdead', 'cfg_subsys_offline', 'cfg_subsys_dead'],
    ['init', 'start', 'init'],
    ['cfg', 'init', 'cfg'],
    ['online', 'cfg', 'online'],
    ['offline', 'online', 'offline'],
    ['dead', 'offline', 'dead']
]

model1 = target()
machine = GM(model=model1,
             states=states,
             transitions=transitions,
             auto_transitions=False,
             initial='start',
             title="Mood Matrix",
             show_conditions=True)
model1.show_graph()

model1.init()
print model1.state
model1.show_graph()
print model1.state
model1.cfg()
print model1.state
model1.online()
print model1.state
model1.show_graph()
