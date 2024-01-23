# vim: ts=4:sw=4
from lib.nodes.block_node import BlockNode
from lib.nodes.variable_node import VariableNode
from lib.values.value import Value


class FunctionNode(BlockNode):
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

    def add_instantiation(self, klass, count=1):
        """ Notes that this function, when called, might instantiate the given Class.
        """
        self.instantiates[klass] = self.instantiates.get(klass, {
            'instanced': 0
        })

        self.instantiates[klass]['instanced'] += count

    def add_instantiations(self, instantiations):
        for klass, info in instantiations.items():
            self.add_instantiation(klass, count=info['instanced'])

    def to_string(self, indent=""):
        lines = []

        # Info about this function
        lines.append(f'{indent}called {self.called} times')

        for condition, count in self.called_conditionally.items():
            lines.append(f'{indent}called {count} times when {condition.values}')

        return lines
