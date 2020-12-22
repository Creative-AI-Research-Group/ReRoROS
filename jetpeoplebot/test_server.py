from random import random
from traitlets import HasTraits, Float, observe
from time import sleep


class Parent:
    def __init__(self):
        print('Parent am init')
        sleep(1)
        rnd = random()
        print('parent rnd = ', rnd)



class Child1(Parent):
    def __init__(self):
        super().__init__()
        print('child 1 init)')
