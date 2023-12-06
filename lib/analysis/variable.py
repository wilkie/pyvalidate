# vim: ts=4:sw=4
from lib.analysis.context import Context

class Variable(Context):
    """ Holds information about a variable.
    """

    def __init__(self, node, parent, annotation):
        super().__init__(node, parent=parent, annotation=annotation)
        self.value = None

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def lookup(self, name, recurse=True):
        # Determine which reference this is
        value = self.value
        prototypes = []
        if value is not None:
            for value_item in value.values:
                if value_item[0] == 'reference':
                    prototypes.append(value_item[1])

        if len(prototypes) > 0:
            for prototype in prototypes:
                subvalue = prototype.lookup(name, recurse=True)

                if subvalue:
                    return subvalue

        if recurse and self.parent:
            return self.parent.lookup(name)

        return None

    def add_call(self, name, method, condition=None):
        value = self.value
        if value is not None:
            for value_item in value.values:
                if value_item[0] == 'reference':
                    reference = value_item[1]
                    reference.add_call(name, method, condition=condition)

    def add_property(self, name, prop):
        value = self.value
        if value is not None:
            for value_item in value.values:
                if value_item[0] == 'reference':
                    reference = value_item[1]
                    reference.add_property(name, prop)

    def to_string(self, indent=""):
        lines = []

        return lines
