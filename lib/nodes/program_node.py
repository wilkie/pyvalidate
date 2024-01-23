# vim: ts=4:sw=4
from lib.nodes.block_node import BlockNode

class ProgramNode(BlockNode):
    """ The main context for the entire program.
    """

    def __init__(self, node):
        super().__init__(node, parent=None)
