# vim: ts=4:sw=4
from lib.analysis.context import Context
from lib.analysis.block import Block
from lib.analysis.method import Method
from lib.analysis.klass import Class
from lib.analysis.variable import Variable
from lib.analysis.value import Value
from lib.analysis.function import Function
from lib.analysis.function_block import FunctionBlock


class Call(Context):
    """ Manages the context around a function call.
    """

    def valueOf(self, callee, text, ast, context, this=None):
        """ Negotate a Value for the given call of this function.

        Call is an AST node representing a CallExpression.
        """

        print('callee!!!!!!!', callee.annotation.get('returns'))

        definition = None
        body = None
        if isinstance(callee, Method):
            # This is a method of a class
            definition = callee.node.value
        else:
            definition = callee.node

        # Assign values to the Variable objects representing the arguments
        # and then continue to negotiate the resulting value.
        callee_context = FunctionBlock(callee.node, callee)

        if this is not None:
            callee_context.add_variable('this', this)

        i = 0
        print('calling', definition)
        for param in definition.params:
            # TODO: annotate the type of the variable
            print('adding', param.name)
            variable = Variable(param, callee, annotation=None)
            variable.set_value(Value.valueOf(self.node.arguments[i], text, ast, context))
            callee.add_variable(param.name, variable)
            i += 1

        # Now, evaluate the return Value by going through the function body
        body = definition.body

        # TODO: add a 'return undefined;' line at the bottom of the function.
        ast._annotate(body, text, ast.ast, callee_context)

        #print('determining value of call')
        #for subnode in body:
        #    Value.valueOf(subnode, text, ast, callee_context)

        # Return the accumulated value by inspecting the
        # return statements.

        # Get possible returns / raises
        value = Value.combine(callee, callee_context.returns, halt_if_true=True)
        print('returned value:')
        print(value.values)

        return value
