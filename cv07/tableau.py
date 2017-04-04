ALPHA = 1
BETA  = 2

class SignedFormula(object):
    def __init__(self, sign, f):
        self.sign = sign
        self.f = f

    @staticmethod
    def T(f):
        """ Create a True signed formula. """
        return SignedFormula(True, f)

    @staticmethod
    def F(f):
        """ Create a False signed formula. """
        return SignedFormula(False, f)

    def neg(self):
        """ Returns a negation of this signed formula. """
        return SignedFormula(not self.sign, self.f)

    def __neg__(self):
        return self.neg()

    def getType(self):
        """ Return tableau type of this signed formula (ALPHA or BETA).

        Depends on the implementation of Formula.getType(sign).
        """
        return self.f.getType(self.sign)

    def subf(self):
        """ Return signed subformulas of this formula in a tableau rule.

        Depends on the implementation of Formula.signedSubfsign).
        """
        return self.f.signedSubf(self.sign)

    def signString(self):
        return 'T' if self.sign else 'F'

    def toString(self):
        return '{} {}'.format(self.signString(), self.f.toString())

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return 'SignedFormula({},{})'.format(
                self.signString(),
                repr(self.f)
        )

T = SignedFormula.T
F = SignedFormula.F

class Tableau(object):
    """ A (propositional) tableau that consists of Node-s. """
    def __init__(self):
        """ Creates an empty tableau. """
        self.root = None
        self.number = 0

    def append(self, parent, node):
        """
        Appends node as a child of parent.

        If parent is None, sets node as the root of the tableau.
        Parent must belong to this tableau!
        """

        if node.children:
            raise ValueError("Can't append nodes with children!")

        if parent is None:
            if self.root is not None:
                raise ValueError("Inserting root node (node.parent == None) into a tableau with a root")
            self.root = node
            self.number = 0
        else:
            if parent.tableau is not self:
                raise ValueError("Parent does not belong to  this tableau!")
            parent.children.append(node)

        self.number += 1
        node.number = self.number
        node.tableau = self

        return node

    def isClosed(self):
        """ Returns True if the tableau is closed. """
        return (self.root is not None) and self.root.isClosed()

    def size(self):
        """ Returns the size (number of formulas) in the tableau. """
        return self.number

    def toString(self):
        if self.root is None:
            return "EMPTY"
        return self.root.printTree()

    def __str__(self):
        return self.toString()

class Node(object):

    def __init__(self, sf, source = None):
        """ Creates a new node.

            sf - the signed formula in this node
            source - reference to the node containing the original formula
                     that this node was created from
                     (None for "input" formulas at the top of the tableau)
        """
        self.sf = sf
        self.number = 0
        self.source = source
        self.closed = False
        self.closedFrom = None
        self.children = []

    def close(self, closedFrom):
        """ Closes this node (and this branch) because it is complemetary
            to closedFrom.
        """
        self.closed = True
        self.closedFrom = closedFrom

    def isClosed(self):
        """ Returns True if the subtree rooted at this node is closed. """
        if self.closed:
            return True

        if self.children:
            return all([ child.isClosed() for child in self.children ])

        return self.closed

    def disown(self):
        """ Removes the node and its children from the tableau it belongs to. """
        for child in self.children:
            child.disown()
        self.tableau = None

    def toString(self):
        return '{}{}'.format(self.label(), " *" if self.closed else "")
    def __str__(self):
        return self.toString()
    def __repr__(self):
        return 'Node< {} >'.format(str(self))

    def label(self):
        nsf = '({}) {}'.format(self.number, str(self.sf))
        if self.source != None:
            return '{} ({})'.format(nsf, self.source.number)
        else:
            return nsf

    def printTree(self):
        return '\n'.join( self._lines() )

    _separator = ' | '

    def _width(self):
        form_wd = len( self.label() )
        children_wd = sum( [ child._width() for child in self.children ] )
        children_wd += len(self._separator) * max(0, len(self.children) - 1)
        return max(form_wd, children_wd)

    def _lines(self):
        width = self._width()

        lines = [ self.label() ]
        if self.closed:
            lines.append( '* [%d,%d]' % (self.number, self.closedFrom.number) )

        if self.children:
            if self.source is None and self.children[0].source is not None:
              lines.append('=' * width)
            elif len(self.children) > 1:
              lines.append('-' * width)
            lines.extend( self._mergeChildLines() )

        return [ line.center(width) for line in lines ]

    def _mergeChildLines(self):
        chLines  = [ child._lines() for child in self.children ]
        ch_widths = [ child._width() for child in self.children ]
        ch_len = len(self.children)
        lines = []
        allEmpty = False

        while not allEmpty:
            allEmpty = True
            lineParts = []
            for i in range(ch_len):
                if len(chLines[i]) > 0:
                    # use an i-th child line and remove it from the list
                    chLine = chLines[i].pop(0)
                    lineParts.append( chLine )
                    allEmpty = False
                else:
                    # i-th child has no more lines, pad with spaces
                    lineParts.append( ' ' * ch_widths[i] )
            if not allEmpty:
                lines.append( self._separator.join(lineParts) )
        return lines

# vim: set sw=4 ts=8 sts=4 et :
