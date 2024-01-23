# vim: ts=4:sw=4
from lib.nodes.structural_node import StructuralNode
from lib.nodes.method_node import MethodNode
from lib.nodes.variable_node import VariableNode
from lib.nodes.function_block_node import FunctionBlockNode
from lib.values.value import Value


class CallNode(StructuralNode):
    """ Manages the context around a function call.
    """

    def valueOf(self, callee, text, ast, context, this=None):
        """ Negotate a Value for the given call of this function.

        Call is an AST node representing a CallExpression.
        """

        definition = None
        body = None
        if isinstance(callee, MethodNode) or callee.node.static:
            # This is a method of a class
            definition = callee.node.value
        else:
            definition = callee.node

        # Assign values to the Variable objects representing the arguments
        # and then continue to negotiate the resulting value.
        callee_context = FunctionBlockNode(callee.node, callee)

        if this is not None:
            callee_context.add_variable('this', this)

        i = 0
        for param in definition.params:
            # TODO: annotate the type of the variable
            variable = VariableNode(param, callee, annotation=None)
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
        return value
