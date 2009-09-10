import random
import garlicsim_wx.misc.vectors as vectors
import garlicsim
import copy

def make_plain_state(*args, **kwargs):
    pass

class Body(object):
    pass

class BodyState(object):
    def __init__(self, position, velocity=None, acceleration=None):
        self.position = position
        self.velocity = velocity or vectors.zeros(3)
        self.acceleration = acceleration or vectors.zeros(3)
    

def make_random_state(*args, **kwargs):
    
    def randomish_vector(x):
        randomish_number = lambda: random.random() * x - (x/2.0)
        return vectors.Vector([randomish_number() for i in range(3)])
    
    def three_randomish_vectors(x):
        return [randomish_vector(y) for y in [x, x/2.0, x/4.0]]
    
    number_of_bodies = 5
    bodies = [Body() for i in range(number_of_bodies)]    
    d = {}
    for body in bodies:
        d[body] = BodyState(*three_randomish_vectors(10))
    
    state = garlicsim.state.State()
    state.bodies = d
    
    return state


def step(old_state, *args, **kwargs):
    new_state = 
    pass


