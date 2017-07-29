import sys

from transitions import Machine
from transitions import State

class Matter(object):
    def __init__(self, start_state):
        print (sys._getframe().f_code.co_name)
        self.start_state_dict = {}
        self.start_state_dict['solid'] = self.entry_solid
        self.start_state_dict['liquid'] = self.entry_liquid
        self.start_state_dict['gas'] = self.entry_gas
        self.start_state_dict['plasma'] = self.entry_plasma
        # the start state entry needs to call explicitely
        print("Calling start state now :- ")
        self.start_state_dict[start_state]()

    def entry_solid(self):
        print (sys._getframe().f_code.co_name)

    def exit_solid(self):
        print (sys._getframe().f_code.co_name)

    def entry_liquid(self):
        print (sys._getframe().f_code.co_name)

    def exit_liquid(self):
        print (sys._getframe().f_code.co_name)

    def entry_gas(self):
        print (sys._getframe().f_code.co_name)

    def exit_gas(self):
        print (sys._getframe().f_code.co_name)

    def entry_plasma(self):
        print (sys._getframe().f_code.co_name)

    def exit_plasma(self):
        print (sys._getframe().f_code.co_name)

lump = Matter('solid')

# And some transitions between states. We're lazy, so we'll leave out
# the inverse phase transitions (freezing, condensation, etc.).
transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' },
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas' },
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas' },
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma' }
]

solid = State(name='solid', on_enter=['entry_solid'], on_exit=['exit_solid'])
liquid = State(name='liquid', on_enter=['entry_liquid'], on_exit=['exit_liquid'])
gas = State(name='gas', on_enter=['entry_gas'], on_exit=['exit_gas'])
plasma = State(name='plasma', on_enter=['entry_plasma'], on_exit=['exit_plasma'])

states=[solid, liquid, gas, plasma]

machine = Machine(lump, states=states, transitions=transitions, initial='liquid')

print lump.state
lump.evaporate()
print lump.state
lump.trigger('ionize')
print "lump.is_ionize() " + str(lump.is_plasma())
print "lump.is_solid() " + str(lump.is_solid())
print lump.state

