# vim: ts=4:sw=4
class Context:
    """ Keeps track of analysis context.

    This is subclassed for different types of context: functions, classes, etc.
    """

    def __init__(self, node, parent=None, annotation=None):
        self.node = node
        self.annotation = annotation or {}
        self.parent = parent
        self.conditions = []
        self.condition = None

    def add_condition(self, value):
        """ Adds the given Value as the condition on which code is now assuming.
        """

        self.conditions.append(self.condition)
        if self.condition is None:
            self.condition = value
        else:
            self.condition = self.condition and value

    def pop_condition(self):
        """ Pops the last condition to have been added to this context.
        """

        self.condition = self.conditions.pop()
        return self.condition

    def get_condition(self):
        """ Gets the condition stack.
        """

        return self.condition

    def to_string(self, indent=""):
        return ""

    def lookup(self, name, recurse=True):
        if recurse and self.parent:
            return self.parent.lookup(name)

        return None

    def __str__(self):
        """ Prints out the context.
        """

        return ('\n').join(self.to_string())
