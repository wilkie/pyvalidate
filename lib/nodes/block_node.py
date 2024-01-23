# vim: ts=4:sw=4
from lib.nodes.structural_node import StructuralNode
from lib.values.raised import Raised


class BlockNode(StructuralNode):
    """ A block within the program.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.declarations = []
        self.raises = []
        self.instantiates = {}

        # TODO: just make use of this some other way
        if parent:
            self.condition = parent.condition

    def get_name(self):
        if hasattr(self.node, 'id') and hasattr(self.node.id, 'name'):
            return self.node.id.name

        return '{}'

    def add_raises(self, exception, message):
        """ Adds the possibility of a raised exception to this context.
        """
        ret = Raised(exception, message, self.condition)
        self.raises.append(ret)
        return ret

    def add_variable(self, name, variable):
        """ Adds the variable declaration to this context.
        """
        self.variables[name] = variable
        self.declarations.append(variable)

    def add_function(self, name, function):
        """ Adds the function declaration to this context.
        """
        self.functions[name] = function
        self.declarations.append(function)

    def add_class(self, name, klass):
        """ Adds the class declaration to this context.
        """
        self.classes[name] = klass
        self.declarations.append(klass)

    def add_instantiation(self, klass, count=1):
        """ Notes that this context might instantiate the given Class.
        """
        if self.parent:
            self.parent.add_instantiation(klass)
        else:
            self.instantiates[klass] = self.instantiates.get(klass, {
                'instanced': 0
            })

            self.instantiates[klass]['instanced'] += count

    def add_instantiations(self, instantiations):
        """ Notes that this context might instantiate the given set of instantiations.
        """
        if self.parent:
            self.parent.add_instantiations(instantiations)
        else:
            for klass, info in instantiations.items():
                self.add_instantiation(klass, count=info['instanced'])

    def add_return(self, value):
        """ Adds the given possible return value for this block.
        """

        from lib.nodes.function_block_node import FunctionBlockNode

        # Find the parent function block
        parent = self.parent
        while parent is not None and not isinstance(parent, FunctionBlockNode):
            parent = parent.parent

        if parent is not None:
            parent.add_return(value)

    def lookup(self, name, recurse=True):
        """ Looks up the given name and returns the information block for it.

        Will return None if the name is not defined in the given context.

        By default, it will also search the context above it.
        """

        if name in self.variables:
            return self.variables[name]

        if name in self.functions:
            return self.functions[name]

        if name in self.classes:
            return self.classes[name]

        if recurse and self.parent:
            return self.parent.lookup(name)

        return None

    def to_string(self, indent=""):
        lines = []

        for name, klass in self.classes.items():
            lines.append(f'{indent}class {name}:')

            lines.extend(klass.to_string(indent + '  '))

        for name, variable in self.variables.items():
            value = variable.get_value()
            type = None
            if value is not None:
                type = value.type()

            lines.append(f'{indent}var {name}: {type}')
            lines.extend(variable.to_string(indent + '  '))

        for name, function in self.functions.items():
            lines.append(f'{indent}fn {name}() -> {function.annotation.get("returns")}')
            lines.extend(function.to_string(indent + '  '))

        for klass, info in self.instantiates.items():
            lines.append(f'{indent}instantiates {klass.get_name()}: {info.get("instanced", 0)}')

        return lines
