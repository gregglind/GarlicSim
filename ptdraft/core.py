import functools
import nib
import time

"""
TODO: in radiation style simulations, how will the simulator know
the history of the particles' movements? Two options. Either
traverse the nibtree, or have that information inside every
nib. Which one should I choose?

Or maybe give two options, one where the simulations gets the
nib and one where it gets the nibnode.
"""


class Simulation(object):
    """
    This is a general class for simulations.
    Bernd-style simulations will inherit from this class.
    Life-Style simulations will also inherit from this class.
    Therefore, this class will be quite general.
    """

    def step(self, *args, **kwargs):
        raise NotImplementedError

    def show(self, *args, **kwargs):
        raise NotImplementedError

    def makeplainnib(self, *args, **kwargs):
        raise NotImplementedError

    def makerandomnib(self, *args, **kwargs):
        raise NotImplementedError

    def step(self, *args, **kwargs):
        raise NotImplementedError

    def compareclockreadings(self,*args,**kwargs):
        raise NotImplementedError #Maybe return None here?


class Playon(object):
    """
    initially each playon will be attached to a specific "simulation";
    later I'll make it able to use several simulations
    """

    def __init__(self,simulationclass):
        self.simulation=simulationclass()
        self.nibtree=nib.NibTree()

    def make_plain_root(self,*args,**kwargs):
        nib=self.simulation.make_plain_nib(*args,**kwargs)
        nib.make_touched()
        return self.root_this_nib(nib)

    def make_random_root(self,*args,**kwargs):
        nib=self.simulation.make_random_nib(*args,**kwargs)
        nib.touched=True
        return self.root_this_nib(nib)

    def root_this_nib(self,nib):
        return self.nibtree.add_nib(nib)

    def step(self,sourcenibnode,t=1):
        newnib=self.simulation.step(sourcenibnode.nib,t)
        return self.nibtree.add_nib(newnib,sourcenibnode)

    def multistep(self,sourcenibnode,t=1,steps=1):
        mynibnode=sourcenibnode
        for i in range(steps):
            mynibnode=self.step(mynibnode,t)
        return mynibnode











"""
class bernd(simulation):
    def step(self):
        print("thing")
    pass
"""