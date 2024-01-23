# vim: ts=4:sw=4

class Reference:
    """ Represents a class instance within the code.
    """

    def __init__(self, node, base_class, annotation=None):
        self.parent = base_class

        self.methods = {}
        self.properties = {}

    def lookup(self, name, recurse=True):
        """ Looks up the given name and returns the information block for it.

        Will return None if the name is not defined in the given context.

        By default, it will also search the context above it.
        """

        if name in self.properties:
            return self.properties[name]

        if name in self.methods:
            return self.methods[name]

        return self.parent.lookup(name, recurse=recurse)

    def add_call(self, name, node, condition=None):
        from lib.analysis.method import Method
        self.methods[name] = self.methods.get(name, Method(self.node, self))
        self.methods[name].add_call(node, condition)

    def add_property(self, name, prop):
        if name not in self.properties:
            self.properties[name] = prop

    def to_string(self, indent=''):
        lines = []

        for method_name in self.parent.methods.keys():
            if method_name in self.methods.keys():
                lines.append(f'{indent}{method_name}()')
                lines.extend(self.methods[method_name].to_string(indent + '  '))

        for prop_name in self.properties.keys():
            # Ignore private properties
            if prop_name.startswith('_'):
                continue

            values = []
            prop = self.properties[prop_name]
            for value in prop.get_value().values:
                values.append(value[1])
            lines.append(f'{indent}{prop_name}: {values}')

        return lines

    def __str__(self):
        return '\n'.join(self.to_string())
