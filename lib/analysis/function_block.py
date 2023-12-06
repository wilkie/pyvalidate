# vim: ts=4:sw=4
from lib.analysis.block import Block


class FunctionBlock(Block):
    """ A block that serves as the main context of a function.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.returns = []

    def add_return(self, value):
        self.returns.append(value)
