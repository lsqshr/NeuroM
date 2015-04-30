'''Generic tree class and iteration functions'''
from itertools import chain, imap, ifilter


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


def is_forking_point(tree):
    '''Is this tree a forking point?'''
    return len(tree.children) > 1


def is_leaf(tree):
    '''Is this tree a leaf?'''
    return len(tree.children) == 0


def is_root(tree):
    '''Is this tree the root node?'''
    return tree.parent is None


def iter_preorder(tree):
    '''Depth-first pre-order iteration of tree nodes'''
    yield tree
    for v in chain(*imap(iter_preorder, tree.children)):
        yield v


def iter_postorder(tree):
    '''Depth-first post-order iteration of tree nodes'''
    for v in chain(*imap(iter_postorder, tree.children)):
        yield v
    yield tree


def iter_upstream(tree):
    '''Iterate from a tree node to the root nodes'''
    t = tree
    while t is not None:
        yield t
        t = t.parent


def iter_segment(tree):
    '''Iterate over segment values

    Segments are parent-child pairs, with the child being the
    center of the iteration
    '''
    return imap(lambda t: (t.parent.value, t.value),
                ifilter(lambda t: t.parent is not None,
                        iter_preorder(tree)))


def iter_leaf(tree):
    '''Iterator to all leaves of a tree'''
    return ifilter(lambda t: len(t.children) == 0, iter_preorder(tree))


def iter_forking_point(tree):
    '''Iterator to forking points. Returns a tree object.'''
    return ifilter(lambda t: len(t.children) > 1,
                   iter_preorder(tree))


def val_iter(iterator):
    '''Iterator adaptor to iterate over Tree.value'''
    return imap(lambda t: t.value, iterator)


def iter_section(tree):
    '''Iterator to sections of a tree.

    Resolves to a tuple of sub-trees forming a section.
    '''
    def get_section(tree):
        '''get the upstream section starting from this tree'''
        ui = iter_upstream(tree)
        sec = [ui.next()]
        for i in ui:
            sec.append(i)
            if is_forking_point(i) or is_root(i):
                break
        sec.reverse()
        return tuple(sec)

    def boundary_node(n):
        '''Is this a section boundary node?'''
        return not is_root(n) and (is_leaf(n) or is_forking_point(n))

    return imap(get_section,
                ifilter(boundary_node, iter_preorder(tree)))