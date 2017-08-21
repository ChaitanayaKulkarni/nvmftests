from transitions.extensions import MachineFactory


class CounterMachine(object):
    """ Target Subsystem State Machine """

    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('counter.png', prog='dot')


class CollectorMachine(object):
    """ Target Subsystem State Machine """

    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('collector.png', prog='dot')


count_states = ['1', '2', '3', 'done']
count_trans = [
    ['increase', '1', '2'],
    ['increase', '2', '3'],
    ['decrease', '3', '2'],
    ['decrease', '2', '1'],
    ['done', '3', 'done'],
    ['reset', '*', '1']
]
counter_class = CounterMachine()

GraphMachine = MachineFactory.get_predefined(graph=True, nested=True,
                                             locked=True)
counter = GraphMachine(model=counter_class,
                       states=count_states,
                       transitions=count_trans,
                       initial='1')
counter_class.show_graph()


states = ['waiting', 'collecting', {'name': 'counting', 'children': counter}]

transitions = [
    ['collect', '*', 'collecting'],
    ['wait', '*', 'waiting'],
    ['count', 'collecting', 'counting_1']
]

collector_class = CollectorMachine()
collector = GraphMachine(model=collector_class,
                         states=states,
                         transitions=transitions,
                         initial='waiting')
collector_class.show_graph()

"""
collector.collect()  # collecting
collector.count()  # let's see what we got
collector.increase()  # counting_2
collector.increase()  # counting_3
collector.done()  # collector.state == counting_done
collector.wait()  # collector.state == waiting
"""
