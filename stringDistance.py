__author__ = 'meyer'
from collections import defaultdict
import gc


def edit_distance(a, b):
    if len(a) < len(b):
        return edit_distance(b, a)
    d = defaultdict(int)
    for i in range(1, len(a)+1):
        d[i, 0] = i
    for j in range(1, len(b) + 1):
        d[0, j] = j

    for j in range(1, len(b) + 1):
        for i in range(1, len(a) + 1):
            if a[i-1] == b[j-1]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + 1)

    return d[len(a), len(b)]


#http://code.activestate.com/recipes/572156-bk-tree/
class BKtree(object):
    """
    BKtree(items, distance, usegc=False): inputs are an iterable of hashable items that
    must allow the next() method too, and a callable that computes the distance (that
    mets the positivity, symmetry and triangle inequality conditions) between two items.

    It allows a fast search of similar items. The indexing phase may be slow,
    so this is useful only if you want to perform many searches.

    It raises a AttributeError if items doesn't have the .next() method.

    It can be used with strings, using editDistance()/editDistanceFast()

    Once initialized, you can retrieve items using xfind/find, giving an item
    and a threshold distance.

    You can disable the GC during the indexing phase to speed it up (default disabled),
    enabling it you may save some memory.
    If you have Psyco you can use it to speed up editDistanceFast.
    You can speed up this class with (but not binding it with Psyco):
    from psyco.classes import __metaclass__
    You can also use the psyco metaclass just for this BKtree class, with psyobj.

    >>> t = BKtree([], distance=editDistanceFast)
    Traceback (most recent call last):
      ...
    AttributeError: 'list' object has no attribute 'next'
    >>> t = BKtree(iter([]), distance=editDistanceFast)
    >>> t.find("hello", 1), t.find("", 0)
    ([], [])

    >>> ws = "abyss almond clump cubic cuba adopt abused chronic abutted cube clown admix almsman"
    >>> t = BKtree(iter(ws.split()), distance=editDistanceFast)
    >>> [len(t.find("cuba", th)) for th in range(7)]
    [1, 2, 3, 4, 5, 9, 13]
    >>> [t.find("cuba", th) for th in range(4)]
    [['cuba'], ['cuba', 'cube'], ['cubic', 'cuba', 'cube'], ['clump', 'cubic', 'cuba', 'cube']]
    >>> [len(t.find("abyss", th)) for th in range(7)]
    [1, 1, 1, 2, 4, 12, 12]
    >>> [t.find("abyss", th) for th in range(4)]
    [['abyss'], ['abyss'], ['abyss'], ['abyss', 'abused']]
    """
    def __init__(self, items, distance, usegc=False):
        self.distance = distance
        self.nodes = {}
        try:
            self.root = items.next()
        except StopIteration:
            self.root = ""
            return

        self.nodes[self.root] = [] # the value is a list of tuples (word, distance)
        gc_on = gc.isenabled()
        if not usegc:
            gc.disable()
        for el in items:
            if el not in self.nodes: # do not add duplicates
                self._addLeaf(self.root, el)
        if gc_on:
            gc.enable()

    def _addLeaf(self, root, item):
        dist = self.distance(root, item)
        if dist > 0:
            for arc in self.nodes[root]:
                if dist == arc[1]:
                    self._addLeaf(arc[0], item)
                    break
            else:
                if item not in self.nodes:
                    self.nodes[item] = []
                self.nodes[root].append((item, dist))

    def find(self, item, threshold):
        "Return an array with all the items found with distance <= threshold from item."
        result = []
        if self.nodes:
            self._finder(self.root, item, threshold, result)
        return result

    def _finder(self, root, item, threshold, result):
        dist = self.distance(root, item)
        if dist <= threshold:
            result.append(root)
        dmin = dist - threshold
        dmax = dist + threshold
        for arc in self.nodes[root]:
            if dmin <= arc[1] <= dmax:
                self._finder(arc[0], item, threshold, result)

    def xfind(self, item, threshold):
        "Like find, but yields items lazily. This is slower than find if you need a list."
        if self.nodes:
            return self._xfinder(self.root, item, threshold)

    def _xfinder(self, root, item, threshold):
        dist = self.distance(root, item)
        if dist <= threshold:
            yield root
        dmin = dist - threshold
        dmax = dist + threshold
        for arc in self.nodes[root]:
            if dmin <= arc[1] <= dmax:
                for node in self._xfinder(arc[0], item, threshold):
                    yield node

def test():
    pass