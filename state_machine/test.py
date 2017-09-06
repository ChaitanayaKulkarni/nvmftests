from transitions.extensions import MachineFactory


class target(object):
    """ """
    def __init__(self):
        self.state_name = ""
        self.name = ""

    def show_graph(self, **kwargs):
        print "state namne " + self.state_name + " name " + self.name
        self.get_graph(**kwargs).draw(self.name + ".png", prog='dot')


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
    # target_ns
    ['target_cfg_subsys_ns_start', 'cfg_subsys_init',
        'cfg_subsys_cfg_ns_start'],

    # target_subsystem
    ['target_cfg_subsys', 'cfg', 'cfg_subsys_start'],
    ['target_cfg_init', 'cfg_subsys_start', 'cfg_subsys_init'],
    ['target_cfg_cfg', 'cfg_subsys_init', 'cfg_subsys_cfg'],
    ['target_cfg_online', 'cfg_subsys_cfg', 'cfg_subsys_online'],
    ['target_cfg_online_success', 'cfg_subsys_online', 'cfg'],
    # target
    ['target_init', 'start', 'init'],
    ['target_cfg', 'init', 'cfg'],
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

i = 0
i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_init()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg_subsys()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg_init()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg_subsys_ns_start()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg_online()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_cfg_online_success()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_init_success()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_offline()
print model1.state

i += 1
model1.name = "target" + str(i)
model1.show_graph()
model1.target_shutdown()
print model1.state
