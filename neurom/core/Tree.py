'''Generic tree class and iteration functions'''
from itertools import chain, imap


class Tree(object):
    '''
    Simple tree class. This is a recursive data structure, with each tree
    holding a value and a list of children trees. Every node is a tree.
    '''
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = list()

    def add_child(self, tree):
        '''Add a child to the list of this tree's children

        This tree becomes the added tree's parent
        '''
        self.children.append(tree)
        tree.parent = self


def iter_preorder(tree):
    '''Depth-first pre-order iteration of tree nodes'''
    yield tree.value
    for v in chain(*imap(iter_preorder, tree.children)):
        yield v


def iter_postorder(tree):
    '''Depth-first post-order iteration of tree nodes'''
    for v in chain(*imap(iter_postorder, tree.children)):
        yield v
    yield tree.value


def iter_upstream(tree):
    t = tree
    while t is not None:
        yield t.value
        t = t.parent