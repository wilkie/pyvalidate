# vim: ts=4:sw=4
from lib.analysis.block import Block
from lib.analysis.value import Value
from lib.analysis.variable import Variable


class Function(Block):
    """ Holds information about a function.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.calls = {}
        self.called = 0
        self.called_conditionally = {}

    def add_call(self, node, condition=None):
        """ Adds a reference to this function being called.
        """

        if node not in self.calls:
            self.calls[node] = node
            if condition is None:
                self.called += 1
            else:
                self.called_conditionally[condition] = self.called_conditionally.get(condition, 0)
                self.called_conditionally[condition] += 1

    def to_string(self, indent=""):
        lines = []

        # Info about this function
        lines.append(f'{indent}called {self.called} times')

        for condition, count in self.called_conditionally.items():
            lines.append(f'{indent}called {count} times when {condition.values}')

        return lines
