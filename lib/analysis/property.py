# vim: ts=4:sw=4
from lib.analysis.context import Context
from lib.analysis.method import Method

class Property(Context):
    """ Holds information about a property (which is up to two methods).
    """

    def __init__(self, node, parent, annotation=None, readable=False, writable=False):
        super().__init__(node, parent=parent, annotation=annotation)
        self.readable = readable
        self.writable = writable
        self.setter = None
        self.getter = None

    def add_setter(self, method):
        """ Adds a Method that acts as a setter.
        """

        self.writable = True
        self.setter = method

    def add_getter(self, method):
        """ Adds a method that acts as a getter.
        """

        self.readable = True
        self.getter = method
