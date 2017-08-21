from transitions.extensions import MachineFactory


class Matter1(object):
    """ """
    def is_hot(self):
        return True

    def is_too_hot(self):
        return False

    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('state1.png', prog='dot')


class Matter2(object):
    """ """
    def is_hot(self):
        return True

    def is_too_hot(self):
        return False

    def show_graph(self, **kwargs):
        self.get_graph(**kwargs).draw('state2.png', prog='dot')

GM = MachineFactory.get_predefined(graph=True, nested=True,
                                             locked=True)

states = ['standing', 'walking',
          {'name': 'caffeinated', 'children': ['dithering', 'running']}]
transitions = [
    ['walk', 'standing', 'walking'],
    ['go', 'standing', 'walking'],
    ['stop', 'walking', 'standing'],
    {'trigger': 'drink', 'source': '*', 'dest': 'caffeinated_dithering',
        'conditions': 'is_hot', 'unless': 'is_too_hot'},
    ['walk', 'caffeinated_dithering', 'caffeinated_running'],
    ['relax', 'caffeinated', 'standing'],
    ['sip', 'standing', 'caffeinated']
]

model1 = Matter1()
machine = GM(model=model1,
             states=states,
             transitions=transitions,
             auto_transitions=False,
             initial='standing',
             title="Mood Matrix",
             show_conditions=True)
model1.show_graph()

model1.walk()
model1.show_graph()
model1.drink()
model1.show_graph()
