import sys

from transitions.extensions import GraphMachine


class TargetNSStateMachine(object):
    def __init__(self, start_state):
        print (sys._getframe().f_code.co_name)
        self.start_state_dict = {}
        self.start_state_dict['start'] = self.entry_start
        self.start_state_dict['init'] = self.entry_init
        self.start_state_dict['running'] = self.entry_running
        self.start_state_dict['dead'] = self.entry_dead

        # the start state entry needs to call explicitely
        print("Calling start state now :- ")
        self.start_state_dict[start_state]()

    def entry_start(self):
        print (sys._getframe().f_code.co_name)

    def exit_start(self):
        print (sys._getframe().f_code.co_name)

    def entry_init(self):
        print (sys._getframe().f_code.co_name)

    def exit_init(self):
        print (sys._getframe().f_code.co_name)

    def entry_running(self):
        print (sys._getframe().f_code.co_name)

    def exit_running(self):
        print (sys._getframe().f_code.co_name)

    def entry_dead(self):
        print (sys._getframe().f_code.co_name)

    def exit_dead(self):
        print (sys._getframe().f_code.co_name)

    def is_valid_start(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_init(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_delete(self):
        print (sys._getframe().f_code.co_name)
        return True

    # graph object is start by the machine
    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('state.png', prog='dot')


states = ['start', 'init', 'run', 'dead']

transitions = [
    {'trigger': 'start', 'source': 'start', 'dest': 'init', 'conditions':
     'is_valid_start'},
    {'trigger': 'init', 'source': 'init', 'dest': 'run', 'conditions':
     'is_valid_init'},
    {'trigger': 'delete', 'source': 'run', 'dest': 'dead', 'conditions':
     'is_valid_delete'},
]


target_ns = TargetNSStateMachine('start')
machine = GraphMachine(model=target_ns,
                       states=states,
                       transitions=transitions,
                       initial='start',
                       title="Target Namespace State Transition Diagram",
                       show_conditions=True)
target_ns.show_graph()

target_ns.trigger('start')
target_ns.trigger('init')
target_ns.trigger('delete')
