from transitions.extensions import MachineFactory


class target(object):
    """ """
    def __init__(self):
        self.state_name = ""

    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw(self.state_name + ".png", prog='dot')


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
                                         'subsys_dead']}

states = ['start', 'init', target_subsys_cfg_states,
          'online', 'offline', 'dead']
transitions = [
    ['subsysinit', 'cfg_subsys_start', 'cfg_subsys_init'],
    ['subsyscfg', 'cfg_subsys_init', 'cfg_subsys_cfg'],
    ['subsysonline', 'cfg_subsys_cfg', 'cfg_subsys_online'],
    ['subsysoffline', 'cfg_subsys_online', 'cfg_subsys_offline'],
    ['subsysdead', 'cfg_subsys_offline', 'cfg_subsys_dead'],
    ['subsys_init_success', 'cfg_subsys_online', 'cfg'],
    ['subsys_init_failure', 'cfg_subsys_cfg', 'cfg_subsys_dead'],
    ['subsys_initfail_exit', 'cfg_subsys_dead', 'cfg'],
    ['target_init', 'start', 'init'],
    ['target_cfg', 'init', 'cfg'],
    ['target_cfg_subsys', 'cfg', 'cfg_subsys_start'],
    ['target_init_success', 'cfg', 'online'],
    ['target_exec_command', 'online', 'online'],
    ['target_init_failure', 'cfg', 'dead'],
    ['target_offline', 'online', 'offline'],
    ['target_shutdown', 'offline', 'dead']
]

model1 = target()
machine = GM(model=model1,
             states=states,
             transitions=transitions,
             auto_transitions=False,
             initial='start',
             title="Mood Matrix",
             show_conditions=True)

model1.state_name = "start"
model1.show_graph()

model1.target_init()
print model1.state
model1.state_name = "target_init"
model1.show_graph()
print model1.state
model1.target_cfg()
print model1.state
model1.state_name = "target_cfg"
model1.show_graph()
model1.target_init_success()
print model1.state
model1.state_name = "target_init_success"
model1.show_graph()
model1.target_offline()
print model1.state
model1.state_name = "target_offline"
model1.show_graph()
model1.target_shutdown()
print model1.state
model1.state_name = "target_dead"
model1.show_graph()
