import sys

from transitions.extensions import GraphMachine


class TargetSubsysStateMachine(object):
    """ Target Subsystem State Machine """
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

    def entry_init(self):
        print (sys._getframe().f_code.co_name)

    def entry_running(self):
        print (sys._getframe().f_code.co_name)

    def entry_dead(self):
        print (sys._getframe().f_code.co_name)

    def is_valid_start(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_init(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_enable(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_disable(self):
        print (sys._getframe().f_code.co_name)
        return True

    def is_valid_delete(self):
        print (sys._getframe().f_code.co_name)
        return True

    # graph object is start by the machine
    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('state.png', prog='dot')


STATES = ['start', 'init', 'run', 'create_ns', 'delete_ns', 'dead']

target_ns = TargetSubsysStateMachine('start')
machine = GraphMachine(model=target_ns,
                       states=STATES,
                       transitions=None,
                       initial='start',
                       title="Target Subsystem State Transition Diagram",
                       show_conditions=True)

machine.add_transition('start', 'start', 'init')
machine.add_transition('init', 'init', 'run')
machine.add_transition('create_ns', 'run', 'create_ns')
machine.add_transition('delete_ns', 'run', 'delete_ns')
machine.add_transition('run', ['create_ns', 'delete_ns'], 'run')

machine.add_transition('delete', 'run', 'dead')
target_ns.show_graph()