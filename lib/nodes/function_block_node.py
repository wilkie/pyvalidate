# vim: ts=4:sw=4
from lib.nodes.block_node import BlockNode


class FunctionBlockNode(BlockNode):
    """ A block that serves as the main context of a function.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.returns = []

    def add_return(self, value):
        self.returns.append(value)
