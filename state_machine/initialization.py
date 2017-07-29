import sys

from transitions import Machine
from transitions import State

class Matter(object):
    pass
    def __init__(self):
        print (sys._getframe().f_code.co_name)

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

lump = Matter()

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
print lump.state

