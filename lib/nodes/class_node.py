# vim: ts=4:sw=4
from lib.nodes.block_node import BlockNode

class ClassNode(BlockNode):
    """ Represents a class within the code.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.instanced = 0
        self.methods = {}
        self.properties = {}

    def name(self):
        """ Get the common name for this class.
        """
        if self.node.id:
            return self.node.id.name

        return None

    def add_instance(self, context):
        """ When this class is instantiated.
        """

        self.instanced += 1
        context.add_instantiation(self)

    def add_call(self, name, node, condition=None):
        # Called a static method
        self.functions[name].add_call(node, condition=condition)

    def add_method(self, name, method):
        """ Adds the annotated method to the class context.
        """

        if name not in self.methods:
            self.methods[name] = method

    def add_property(self, name, prop):
        """ Adds the annotated property to the class context.
        """

        if name not in self.properties:
            self.properties[name] = prop

    def lookup(self, name, recurse=True):
        """ Looks up the given name and returns the information block for it.

        Will return None if the name is not defined in the given context.

        By default, it will also search the context above it.
        """

        if name in self.methods:
            return self.methods[name]

        if name in self.properties:
            return self.properties[name]

        return super().lookup(name, recurse=recurse)

    def to_string(self, indent=""):
        lines = []

        lines.append(f'{indent}constructed: {self.instanced} times')

        for method_name, method in self.functions.items():
            lines.append(f'{indent}static {method_name}() -> {method.annotation.get("returns")}')
            lines.extend(method.to_string(indent + '  '))

        for method_name, method in self.methods.items():
            lines.append(f'{indent}{method_name}() -> {method.annotation.get("returns")}')
            lines.extend(method.to_string(indent + '  '))

        for prop_name, prop in self.properties.items():
            access = []
            if prop.readable:
                access.append('get')
            if prop.writable:
                access.append('set')
            lines.append(f'{indent}{"/".join(access)} {prop_name}')

        return lines
