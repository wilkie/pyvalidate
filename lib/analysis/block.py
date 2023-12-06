# vim: ts=4:sw=4
from lib.analysis.context import Context
from lib.analysis.raised import Raised


class Block(Context):
    """ A block within the program.
    """

    def __init__(self, node, parent, annotation=None):
        super().__init__(node, parent=parent, annotation=annotation)
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.declarations = []
        self.raises = []
        # TODO: just make use of this some other way
        if parent:
            self.condition = parent.condition

    def add_raises(self, exception, message):
        ret = Raised(exception, message, self.condition)
        self.raises.append(ret)
        return ret

    def add_variable(self, name, variable):
        self.variables[name] = variable
        self.declarations.append(variable)

    def add_function(self, name, function):
        self.functions[name] = function
        self.declarations.append(function)

    def add_class(self, name, klass):
        self.classes[name] = klass
        self.declarations.append(klass)

    def add_return(self, value):
        """ Adds the given possible return value for this block.
        """

        from lib.analysis.function_block import FunctionBlock

        # Find the parent function block
        parent = self.parent
        while parent is not None and not isinstance(parent, FunctionBlock):
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

        return lines
