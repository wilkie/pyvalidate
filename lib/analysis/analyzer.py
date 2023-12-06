# vim: ts=4:sw=4
import re

from functools import partial

from esprima import parseScript

from lib.analysis.program import Program
from lib.analysis.raised import Raised
from lib.analysis.property import Property
from lib.analysis.block import Block
from lib.analysis.function_block import FunctionBlock
from lib.analysis.variable import Variable
from lib.analysis.function import Function
from lib.analysis.method import Method
from lib.analysis.klass import Class
from lib.analysis.value import Value


class Analyzer:
    """
    """

    DOCSTRING_RE = r'@(?P<token>[a-zA-Z]+)(?:\s+{(?P<type>[a-zA-Z]+)})?(?:\s+(?P<description>.+))?'

    def __init__(self, code):
        self.code = code
        self.precode = []
        self.ast = None
        self.context = None

        self.docstring_re = None

    def augment(self, code):
        """ Adds some pre-code to reveal the type information necessary to
            understand the rest of the code.
        """

        self.precode.append(code)

    def annotate(self):
        """ Go through and annotate the variables with their types.
        """

        self.parse()

        # Go through the precode and annotate the functions there
        print("reading precodeast")
        self._annotate(self.precodeast, self.precodetext)
        print("reading code", self.context.functions)
        self._annotate(self.ast, self.text, self.ast, self.context)

        return self.context

    def parseDocstring(self, comment: str):
        """ Parses a JavaScript docstring.

        This function should be able to handle block comments with starting
        asterisks, which is common in JSDoc descriptions.

        :param comment: The block comment string which may include asterisks.
        :returns: A set of fields describing the code block based on the docstring.
        :rtype: dict
        """

        ret = {}

        self.docstring_re = self.docstring_re or re.compile(Analyzer.DOCSTRING_RE)
        for line in comment.split('\n'):
            line = line.strip()
            match = re.search(self.docstring_re, line)
            if match is None: continue

            if match['token'] == 'returns':
                ret['returns'] = ret.get('returns', {})
                for key in ['type', 'description']:
                    try:
                        ret['returns'][key] = match[key]
                    except IndexError:
                        pass

        print("parsed docstring:", ret)
        return ret

    def _annotate(self, node, text, ast=None, context=None):
        # The initial node is the root of the AST
        if ast is None:
            # We are passed the AST root
            ast = node

        # The initial context is empty
        if context is None:
            context = Program(ast)
            self.context = context

        # Go through the nodes
        if node.type == "Program":
            for subnode in node.body:
                self._annotate(subnode, text, ast, context)
        elif node.type == "ClassDeclaration":
            # Create the class
            klass = Class(node, parent=context)
            if node.body:
                self._annotate(node.body, text, ast, klass)

            context.add_class(node.id.name, klass)
        elif node.type == "ClassBody":
            for subnode in node.body:
                self._annotate(subnode, text, ast, context)
        elif node.type == "MethodDefinition":
            # Add method to class
            annotation = self._annotateFunction(node, text, ast, context)
            method = Method(node, parent=context, annotation=annotation)

            name = None
            if node.key:
                name = node.key.name

            if node.kind == "set" or node.kind == "get":
                # Property
                # See if this property already exists
                prop = (context.properties or {}).get(name)

                if not (prop and isinstance(prop, Property)):
                    # Create the property
                    prop = Property(node, writable=True, parent=context, annotation=annotation)
                if node.kind == "set":
                    prop.add_setter(method)
                elif node.kind == "get":
                    prop.add_getter(method)

                context.add_property(name, prop)
            elif node.kind == "get":
                # Property (readable)
                # See if this property already exists as a setter
                prop = (context.properties or {}).get(name)
                if prop and isinstance(prop, Property):
                    # Augment the existing property
                    prop.readable = True
                else:
                    # Create the property
                    prop = Property(node, readable=True, parent=context, annotation=annotation)
                context.add_property(name, prop)
            else:
                context.add_method(name, method)
        elif node.type == "FunctionDeclaration":
            # Determine return type for the function, if any
            annotation = self._annotateFunction(node, text, ast, context)
            function = Function(node, parent=context, annotation=annotation)
            context.add_function(node.id.name, function)

            # If we do not have a return type, we might want to look at the
            # function body and try to determine this.
            # So, we will create the function_context for this purpose
            function_context = FunctionBlock(node, function)
            for param in node.params:
                # TODO: annotate the type of the variable
                print('adding base param', param.name)
                variable = Variable(param, function, annotation=[])
                variable.set_value(Value(param, kind='variant', value=[]))
                function_context.add_variable(param.name, variable)


            # Initialize a new context and annotate the function body
            if node.body:
                self._annotate(node.body, text, ast, function_context)
        elif node.type == "VariableDeclaration":
            # Determine the type of the variable from its initialization
            for declaration in node.declarations:
                # And also call the normal annotate on it
                self._annotate(declaration, text, ast, context)
        elif node.type == "VariableDeclarator":
            # Annotate the init expression
            annotation = self._annotateVariable(node, text, ast, context)

            print("found variable", node.id.name, "of type", annotation.get('type'))

            variable = Variable(node, parent=context, annotation=annotation)
            context.add_variable(node.id.name, variable)
            if node.init:
                # Retain the initial value of the variable
                value = self._valueOf(node.init, text, ast, context)
                print('returned value', value)

                # Set the value
                variable.set_value(value)

                self._annotate(node.init, text, ast, context)
        elif node.type == "CallExpression":
            print('calling bare!!')
            self._valueOf(node, text, ast, context)
        elif node.type == "BlockStatement":
            block = Block(node, parent=context)
            for subnode in node.body:
                self._annotate(subnode, text, ast, block)
        elif node.type == "ReturnStatement":
            # Get the value of the inner argument
            value = self._valueOf(node.argument, text, ast, context)

            # Capture the possible return
            if value:
                print('return', value.values, context, context.parent.annotation.get('returns'))
                context.add_return(value)

            # Return the value of this expression
            return value
        elif node.type == "IfStatement":
            # This is a divergence... determine the condition
            test = self._valueOf(node.test, text, ast, context)
            if test is None:
                print('hm')
                print(node.test)

            if test.false():
                # If it is always False, do not continue
                # This is dead code
                return None

            # Add the condition while we parse the value of the
            # if block.
            if node.consequent:
                print('ok test', test)
                context.add_condition(test)
                self._annotate(node.consequent, text, ast, context)
                # Pop the condition (tho, we worry about the else if)
                print('pop')
                context.pop_condition()
        elif node.type == "ExpressionStatement":
            return self._valueOf(node.expression, text, ast, context)

        return context

    def _annotateFunction(self, node, text, ast, context):
        """ Takes a node of the given AST and attempts to annotate the function.

        This means it will try to determine what the return type of the function
        might be.
        """

        annotation = {}

        # Get the comments for this function
        for comment in ast.comments:
            while (text[comment.range[1] + 1].isspace()):
                comment.range[1] += 1
            if comment.range[1] == node.range[0] - 1:
                if node.type == "MethodDefinition":
                    print("found comment for", node.key.name)
                else:
                    print("found comment for", node.id.name)
                doc = self.parseDocstring(comment.value)
                if 'returns' in doc:
                    annotation['returns'] = doc['returns']['type']

        return annotation

    def _annotateVariable(self, node, text, ast, context):
        ret = {}

        # Look if it is initialized, and if so, determine the type of that
        # expression and assign it to the variable's type
        if node.init:
            typeOf = self._typeOf(node.init, ast, context)
            if typeOf is not None:
                ret['type'] = typeOf

        return ret

    def _typeOf(self, node, ast, context):
        """ Returns the type of this expression, if known.
        """

        if node.type == "CallExpression":
            print("type of callexpression")
            # Function call
            info = context.lookup(node.callee.name)
            if info and info.annotation.get('returns'):
                return info.annotation['returns']

        return None

    def _valueOf(self, node, text, ast, context):
        """ Returns the value of this expression.

        It will attempt to determine the exact value including the type.
        """

        return Value.valueOf(node, text, self, context)

    def _parse(self, code):
        self._last_comment = ""
        def callback(self, node, metadata):
            if node.type == "BlockComment":
                self._last_comment = "hi"
            else:
                if self._last_comment != "":
                    print(node.type)
                self._last_comment = ""

        return parseScript(code, { 'range': True, 'tolerant': True, 'comment': True, 'loc': True }, partial(callback, self))

    def parse(self):
        if self.ast is not None:
            return self.ast

        code = ""
        for precode in self.precode:
            code += precode
        self.precodetext = code
        self.precodeast = self._parse(code)

        code = self.code
        self.ast = self._parse(code)
        self.text = code
        #print(self.precodeast)
        #print(self.ast)

        return self.ast

    def __str__(self):
        def node_to_str(node, indent):
            lines = []
            lines.append(f"type: {node.type}")

            return '\n'.join(lines)

        self.parse()
        print(self.precodeast)
        print(self.ast)
        return node_to_str(self.ast, "")
