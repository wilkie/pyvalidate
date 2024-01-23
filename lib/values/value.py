# vim: ts=4:sw=4
import math


from lib.nodes.structural_node import StructuralNode
from lib.nodes.variable_node import VariableNode

from lib.values.reference import Reference
from lib.values.raised import Raised


class Value:
    """ Represents the abstract (or exact) value of some expression.

    It might be a set of possibilities.
    """

    def __init__(self, node, kind=None, value=None, condition=None):
        """ Construct a Value object with the given initial kind and value.

        The initial `value` can be a tuple to depict a range of possible values.
        """

        self.node = node
        self.values = []
        if kind is not None:
            self.values = [(kind, value, condition,)]

    def __hash__(self):
        return str(self).__hash__()

    @staticmethod
    def combine(node, values, halt_if_true=False):
        """ Combine an array of possible Value objects into a single one.

        This is generally used for the value of a function call. It can be a
        variety of possible things depending on the code flow.
        """

        # We may need to coerce the values to the annotated type
        ret_type = None

        # If this is an internal representation of a node, we have a possible
        # annotation of its return type
        if isinstance(node, StructuralNode):
            ret_type = node.annotation.get('returns')
        else:
            # Otherwise, this is a normal parser node of the function definition
            # which might contain its return type.
            pass

        ret = Value(node)
        for value in values:
            for value_item in value.values:
                ret.values.append(value_item)
                condition = value_item[2]
                if halt_if_true and (condition is None or condition.true()):
                    return Value.influence(ret_type, ret)

        return Value.influence(ret_type, ret)

    @staticmethod
    def influence(new_type, value):
        """ Influences the Value, if it might, to reflect the given type.

        This will push variants to be a particular value type.

        This will also tag numbers to be random.
        """

        if new_type is None:
            return value

        ret = Value(value.node)

        for value_item in value.values:
            old_type = value_item[0]
            old_value = value_item[1]
            coerced_type = old_type

            if new_type == 'random':
                coerced_type = new_type

                # If the current value is not a range, then make it one.
                if not isinstance(old_value, list):
                    old_value = [0.0, 1.0]

            ret.values.append((coerced_type, old_value, value_item[2],))

        return ret

    @staticmethod
    def coerce(new_type, value):
        """ Creates a new Value, if necessary, to represent the given value with
        the new given type.
        """

        ret = Value(value.node)

        for value_item in value.values:
            old_type = value_item[0]
            coerced_type = old_type

            if new_type == 'random':
                coerced_type = new_type

            ret.values.append((coerced_type, value_item[1], value_item[2],))

        return ret

    def type(self):
        """ Get a collection of possible types this variable contains.
        """

        ret = []

        for value in self.values:
            type = value[0]
            if type == 'reference':
                classname = value[1].parent.node.id.name
                type = f'@{classname}'

            if type not in ret:
                ret.append(type)

        return ret

    def false(self):
        """ Determines if this Value is always Falsey.
        """
        is_false = True
        for value in self.values:
            # If any non-raised value is truthy, we return False
            if value[1] and value[0] != 'raised':
                is_false = False
                break

        return is_false

    def true(self):
        """ Determines if this Value is always Truthy.
        """
        is_true = True
        for value in self.values:
            # If it possibly raises or any value is falsey, we return False
            if value[0] == 'raised' or not value[1]:
                is_true = False
                break

        return is_true

    def performBinaryOperation(self, b, operation):
        # Take all possible values and reflect what happens when we add the
        # given value to it.

        # Any raised values propagate

        ret = Value(self.node)
        for lh in self.values:
            lh_type = lh[0]

            for rh in b.values:
                # Determine new type
                rh_type = rh[0]

                # Assume new type is the left-hand type
                new_type = lh_type
                l = lh[1]
                r = rh[1]

                # Until proven otherwise
                if lh_type == 'raised':
                    r = l
                    new_type = 'raised'
                elif rh_type == 'raised':
                    l = r
                    new_type = 'raised'
                elif lh_type == 'variant':
                    new_type = rh_type
                elif lh_type == 'float' or rh_type == 'float':
                    new_type = 'float'
                elif lh_type == 'bool' and rh_type != 'bool':
                    new_type = rh_type

                # Coerce values

                # Any float in the equation becomes a float
                if new_type == 'float' and new_type != lh_type:
                    if lh_type == 'variant':
                        l = 0.0
                    l = float(l)
                elif new_type == 'int' and new_type != lh_type:
                    if lh_type == 'variant':
                        l = 0
                    l = int(l)

                # Any float in the equation becomes a float
                if new_type == 'float' and new_type != rh_type:
                    if rh_type == 'variant':
                        r = 0.0
                    r = float(r)
                elif new_type == 'int' and new_type != rh_type:
                    if rh_type == 'variant':
                        r = 0
                    r = int(r)

                new_value = l
                if new_type != 'variant' and new_type != 'raised':
                    if isinstance(l, list):
                        # Two dimensional set of values
                        if isinstance(r, list):
                            pass
                        else:
                            new_value = list(map(lambda x: operation(x, r), l))

                            # Range has collapsed into a single value
                            if new_value[0] == new_value[1]:
                                new_value = new_value[0]
                    elif isinstance(r, list):
                        # Two dimensional set of values
                        if isinstance(l, list):
                            pass
                        else:
                            new_value = list(map(lambda x: operation(l, x), r))
                            # Range has collapsed into a single value
                            if new_value[0] == new_value[1]:
                                new_value = new_value[0]
                    else:
                        new_value = operation(l, r)

                ret.values.append((new_type, new_value, lh[2],))
        return ret

    def performUnaryOperation(self, operation):
        # Take all possible values and reflect what happens when we add the
        # given value to it.
        ret = Value(self.node)
        for lh in self.values:
            # Determine new type
            ret.values.append((lh[0], operation(lh[1]), lh[2],))
        return ret

    def __add__(self, b):
        """ Adds two Value objects together.
        """

        return self.performBinaryOperation(b, lambda a, b: a + b)

    def __sub__(self, b):
        """ Subtracts one Value object from another.
        """

        return self.performBinaryOperation(b, lambda a, b: a - b)

    def __mul__(self, b):
        """ Multiplies two Value objects together.
        """

        return self.performBinaryOperation(b, lambda a, b: a * b)

    def __truediv__(self, b):
        """ Divides two Value objects.
        """

        return self.performBinaryOperation(b, lambda a, b: a / b)

    def __floordiv__(self, b):
        """ Divides two Value objects (flooring the result).
        """

        return self.performBinaryOperation(b, lambda a, b: a // b)

    def __mod__(self, b):
        """ Yields the remainder from division.
        """

        return self.performBinaryOperation(b, lambda a, b: a % b)

    def __pow__(self, b):
        """ Raises one Value to another
        """

        return self.performBinaryOperation(b, lambda a, b: a ** b)

    def __rshift__(self, b):
        """ Performs a binary right shift.
        """

        return self.performBinaryOperation(b, lambda a, b: a >> b)

    def __lshift__(self, b):
        """ Performs a binary left shift.
        """

        return self.performBinaryOperation(b, lambda a, b: a << b)

    def __and__(self, b):
        """ Performs a logical 'and' of the two Value objects.
        """

        return self.performBinaryOperation(b, lambda a, b: a and b)

    def __or__(self, b):
        """ Performs a logical 'or' of the two Value objects.
        """

        return self.performBinaryOperation(b, lambda a, b: a or b)

    def __xor__(self, b):
        """ Performs a bitwise 'xor' of the two Value objects.
        """

        return self.performBinaryOperation(b, lambda a, b: a ^ b)

    def __not__(self):
        return self.performUnaryOperation(lambda a: not a)

    def __neg__(self):
        return self.performUnaryOperation(lambda a: -a)

    def __pos__(self):
        return self.performUnaryOperation(lambda a: +a)

    def __invert__(self):
        return self.performUnaryOperation(lambda a: ~a)

    def __lt__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a < b)

    def __gt__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a > b)

    def __le__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a <= b)

    def __ge__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a >= b)

    def __eq__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a == b)

    def __ne__(self, b):
        return self.performBinaryOperation(b, lambda a, b: a != b)

    @staticmethod
    def valueOf(node, text, ast, context=None, base=None):
        """ Determine the value of the given subtree rooted at the given node.
        """

        from lib.nodes.property_node import PropertyNode

        if base is None:
            base = node

        # TODO: return a complex type (Value?) that holds the value and the
        # type of the expression. Perhaps, a range of possible values.
        if node.type == "BlockStatement":
            # TODO: move this to Block.valueOf
            value = None
            for subnode in node.body:
                value = Value.valueOf(subnode, text, ast, context)

            return value

        if node.type == "Identifier":
            # Lookup the Value currently representing the named identifier
            variable = context.lookup(node.name)
            if variable is None:
                return None
            return variable.get_value()

        if node.type == "ExpressionStatement":
            # Recursively determine the value of the expression
            return Value.valueOf(node.expression, text, ast, context)
        
        if node.type == "AssignmentExpression":
            # What is the left-hand side?
            this = context
            prop = None
            if node.left.type == "MemberExpression":
                # Look up reference
                if node.left.object.type == "ThisExpression":
                    this = context.lookup('this')
                else:
                    this = context.lookup(node.left.object.name)
                prop = this.lookup(node.left.property.name)
            else:
                # A normal variable
                prop = context.lookup(node.left.name)

            # We only care about the value of the right-hand side
            value = Value.valueOf(node.right, text, ast, context)

            # Now, we want to set the variable state to that value

            # If the property does not exist, we must create it
            if prop is None:
                prop = VariableNode(node.left.property, this, annotation=[])
                this.add_property(node.left.property.name, prop)

            if isinstance(prop, PropertyNode):
                prop = VariableNode(node.left.property, prop, annotation=[])
                this.add_property(node.left.property.name, prop)

            prop.set_value(value)

            # The expression itself has the assigned value
            return value

        if node.type == "CallExpression":
            # We then need to negotiate the function value
            from lib.nodes.call_node import CallNode
            from lib.nodes.class_node import ClassNode
            from lib.nodes.function_node import FunctionNode

            # First, determine the callee context

            # Go through member listing, if it exists
            this = None
            body = None
            if node.callee.type == "MemberExpression":
                # Look up reference
                this = context.lookup(node.callee.object.name)
                if this is None:
                    # Unknown reference
                    # Always a runtime error while evaluating this expression
                    raised = context.add_raises("ReferenceError", f'{node.callee.object.name} is not defined')
                    return Value(node, kind='raised', value=raised, condition=context.condition)

                callee = this.lookup(node.callee.property.name)

                # Add a reference to it being called in this context

                # Is this a static method?
                if not isinstance(callee, FunctionNode):
                    # It is indeed an instance method
                    this.add_call(node.callee.property.name, node, condition=context.condition)
            else:
                # A normal function
                callee = context.lookup(node.callee.name)

            # The function or member lookup failed
            if callee is None:
                return None

            # We want to determine if the function call is the constructor
            constructing = False

            # The constructor is essentially a call on the class itself
            if isinstance(callee, ClassNode):
                # Keep track of the possible instantiations within the current context
                constructing = True

                # Create an instanced context
                base_class = callee
                instance = Reference(node, base_class, base_class.annotation)

                # Look up the possible constructor method
                callee = base_class.lookup('constructor')

                # Create a reference value
                this = Value(node, kind='reference', value=instance, condition=context.condition)

                # Make a note in the class annotation that an instance was created
                # and the context within which it was created.
                base_class.add_instance(context)

                # If there is no constructor, we still return 'this'
                # No need to go through the constructor
                if callee is None:
                    return this
            elif isinstance(callee, FunctionNode):
                # Normal function / static method call
                callee.add_call(node.callee, condition=context.condition)

                # Add instantiations this call makes
                context.add_instantiations(callee.instantiates)

            # Analysis of the possible values
            value = CallNode(node).valueOf(callee, text, ast, context)

            # If this is a constructor call, the value is always the reference
            # and not any value returned by the function body of the constructor.
            if constructing:
                return this

            # Otherwise, we return the aggregate value
            return value

        if node.type == "MemberExpression":
            # Dereference a class instance for a variable
            reference = context.lookup(node.object.name)
            return reference.lookup(node.property.name).get_value()

        if node.type == "UnaryExpression":
            if node.operator == "-":
                # Negate
                return -Value.valueOf(node.argument, text, ast, context, base)
            elif node.operator == "+":
                # Positive
                return +Value.valueOf(node.argument, text, ast, context, base)

        if node.type == "BinaryExpression":
            left = Value.valueOf(node.left, text, ast, context)
            if left is None:
                print('left is none')
                print(node.left)
            right = Value.valueOf(node.right, text, ast, context)

            if node.operator == "+":
                return left + right
            elif node.operator == "-":
                return left - right
            elif node.operator == "*":
                return left * right
            elif node.operator == "/":
                return left / right
            elif node.operator == "<":
                return left < right
            elif node.operator == ">":
                return left > right

        if node.type == "Literal":
            # This is the literal value
            if isinstance(node.value, int):
                return Value(node, 'int', node.value, context.condition)

            if isinstance(node.value, float):
                return Value(node, 'float', node.value, context.condition)

            if isinstance(node.value, str):
                return Value(node, 'string', node.value, context.condition)

        return None
