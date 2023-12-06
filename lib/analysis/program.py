# vim: ts=4:sw=4
from lib.analysis.block import Block

class Program(Block):
    """ The main context for the entire program.
    """

    def __init__(self, node):
        super().__init__(node, parent=None)
