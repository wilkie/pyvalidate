# vim: ts=4:sw=4
class StructuralNode:
    """ Keeps track of analysis context.

    This is subclassed for different types of context: functions, classes, etc.
    """

    def __init__(self, node, parent=None, annotation=None):
        self.node = node
        self.annotation = annotation or {}
        self.parent = parent
        self.conditions = []
        self.condition = None
        self.children = {}
        self.raised = {}

        if parent:
            parent.add_child(node, self)

    def find(self, node):
        """ Finds the context defined by the given node.
        """
        return self.children.get(f"{node.range[0]}.{node.range[1]}", None)

    def add_raised(self, raised):
        self.raised[raised.exception] = self.raised.get(raised.exception, [])
        self.raised[raised.exception].append(raised)

        if self.parent:
            self.parent.add_raised(raised)

    def add_child(self, node, context):
        """ Adds the given child.
        """

        self.children[f"{node.range[0]}.{node.range[1]}"] = context

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
        """ Lookup a context by its name.
        """

        if recurse and self.parent:
            return self.parent.lookup(name)

        return None

    def __str__(self):
        """ Prints out the context.
        """

        return ('\n').join(self.to_string())
