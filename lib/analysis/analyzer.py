# vim: ts=4:sw=4
import re

from functools import partial

from esprima import parseScript

# Structural Nodes
from lib.nodes.program_node import ProgramNode
from lib.nodes.block_node import BlockNode
from lib.nodes.variable_node import VariableNode
from lib.nodes.function_node import FunctionNode
from lib.nodes.method_node import MethodNode
from lib.nodes.property_node import PropertyNode
from lib.nodes.class_node import ClassNode

# Values
from lib.values.value import Value
from lib.values.raised import Raised


class Analyzer:
    """
    """

    # Regular expression to parse @<token> sequences as part of jsdoc strings.
    DOCSTRING_RE = r'@(?P<token>[a-zA-Z]+)(?:\s+{(?P<type>[a-zA-Z]+)})?(?:\s+(?P<description>.+))?'

    def __init__(self, code):
        """ Constructs a full analysis context.
        """
        self.code = code
        self.precode = []
        self.ast = None
        self.precodeast = None
        self.context = None
        self.docstring_re = None

    def augment(self, code):
        """ Adds some pre-code to reveal the type information necessary to
            understand the rest of the code.
        """
        self.precode.append(code)

        # Invalidate the precode AST
        self.precodeast = None

    def annotate(self, reparse=False):
        """ Go through and annotate the variables with their types.
        """

        # If requested, throw away the old structure
        if reparse:
            self.ast = None

        # Parse all code. This stores its results in AST properties
        self._parse()

        # Go through all ASTs and annotate functions, classes, etc
        self._expand(self.precodeast, self.precodetext)
        self._expand(self.ast, self.text, self.ast, self.context)

        # Do runtime analysis
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

        # Lazy compile the regular expression
        self.docstring_re = self.docstring_re or re.compile(Analyzer.DOCSTRING_RE)

        # Take the comment block and split by line searching for jsdoc context.
        for line in comment.split('\n'):
            # Match against the expression
            line = line.strip()
            match = re.search(self.docstring_re, line)

            # Skip when no match was found
            if match is None: continue

            # Parse out the @returns token
            if match['token'] == 'returns':
                ret['returns'] = ret.get('returns', {})
                for key in ['type', 'description']:
                    try:
                        ret['returns'][key] = match[key]
                    except IndexError:
                        pass

        # Return a dict containing metadata representing the docstrings
        return ret

    def _expand(self, node, text, ast=None, context=None):
        """ Determines the structural aspects of the code.
        """

        # The initial node is the root of the AST
        if ast is None:
            # We are passed the AST root
            ast = node

        # The initial context is empty
        if context is None:
            context = ProgramNode(ast)
            self.context = context

        # Go through the nodes
        if node.type == "Program":
            for subnode in node.body:
                self._expand(subnode, text, ast, context)

        elif node.type == "ClassDeclaration":
            # Create the class
            klass = ClassNode(node, parent=context)
            if node.body:
                self._expand(node.body, text, ast, klass)

            context.add_class(node.id.name, klass)

        elif node.type == "ClassBody":
            for subnode in node.body:
                self._expand(subnode, text, ast, context)

        elif node.type == "MethodDefinition":
            # Add method to class
            annotation = self._annotateFunction(node, text, ast, context)

            if node.static:
                method = FunctionNode(node, parent=context, annotation=annotation)
            else:
                method = MethodNode(node, parent=context, annotation=annotation)

            name = None
            if node.key:
                name = node.key.name

            if node.static:
                context.add_function(name, method)
            elif node.kind == "set" or node.kind == "get":
                # Property
                # See if this property already exists
                prop = (context.properties or {}).get(name)

                if not (prop and isinstance(prop, PropertyNode)):
                    # Create the property
                    prop = PropertyNode(node, writable=True, parent=context, annotation=annotation)
                if node.kind == "set":
                    prop.add_setter(method)
                elif node.kind == "get":
                    prop.add_getter(method)

                context.add_property(name, prop)
            elif node.kind == "get":
                # Property (readable)
                # See if this property already exists as a setter
                prop = (context.properties or {}).get(name)
                if prop and isinstance(prop, PropertyNode):
                    # Augment the existing property
                    prop.readable = True
                else:
                    # Create the property
                    prop = PropertyNode(node, readable=True, parent=context, annotation=annotation)
                context.add_property(name, prop)
            else:
                context.add_method(name, method)

        elif node.type == "FunctionDeclaration":
            # Determine return type for the function, if any
            annotation = self._annotateFunction(node, text, ast, context)
            function = FunctionNode(node, parent=context, annotation=annotation)
            context.add_function(node.id.name, function)

        elif node.type == "BlockStatement":
            block = Block(node, parent=context)
            for subnode in node.body:
                self._expand(subnode, text, ast, block)

        return context

    def _annotate(self, node, text, ast, context):
        """ Annotates the logical aspects of the code based on the structure provided.
        """

        # Go through the nodes
        if node.type == "Program":
            for subnode in node.body:
                self._annotate(subnode, text, ast, context)

        elif node.type == "VariableDeclaration":
            # Determine the type of the variable from its initialization
            for declaration in node.declarations:
                # And also call the normal annotate on it
                self._annotate(declaration, text, ast, context)

        elif node.type == "VariableDeclarator":
            # Annotate the init expression
            annotation = self._annotateVariable(node, text, ast, context)

            variable = VariableNode(node, parent=context, annotation=annotation)
            context.add_variable(node.id.name, variable)
            if node.init:
                # Retain the initial value of the variable
                value = self._valueOf(node.init, text, ast, context)

                # Set the value
                variable.set_value(value)

        elif node.type == "CallExpression":
            self._valueOf(node, text, ast, context)

        elif node.type == "BlockStatement":
            block = context.find(node)
            if block is None:
                block = BlockNode(node, parent=context)
            for subnode in node.body:
                self._annotate(subnode, text, ast, block)

        elif node.type == "ReturnStatement":
            # Get the value of the inner argument
            value = self._valueOf(node.argument, text, ast, context)

            # Capture the possible return
            if value:
                context.add_return(value)

            # Return the value of this expression
            return value

        elif node.type == "IfStatement":
            # This is a divergence... determine the condition
            test = self._valueOf(node.test, text, ast, context)

            if test is None or test.raised():
                # The expression could not be evaluated.
                # Maybe it raised?
                return None

            # Dead code detection
            if test.false():
                # If it is always False, do not continue
                # This is dead code
                return None

            # Add the condition while we parse the value of the
            # if block.
            if node.consequent:
                context.add_condition(test)
                self._annotate(node.consequent, text, ast, context)

                # Pop the condition (tho, we worry about the else if)
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

    def _parse(self):
        if self.precodeast is None:
            code = ""
            for precode in self.precode:
                code += precode
            self.precodetext = code
            self.precodeast = parseScript(code, {
                'range': True, 'tolerant': True, 'comment': True, 'loc': True
            })

        if self.ast is not None:
            return self.ast

        code = self.code
        self.ast = parseScript(code, {
            'range': True, 'tolerant': True, 'comment': True, 'loc': True
        })
        self.text = code

        return self.ast

    def __str__(self):
        """ Print the Semantic Information Tree.
        """

        def node_to_str(node, indent):
            lines = []
            lines.append(f"type: {node.type}")

            return '\n'.join(lines)

        self._parse()
        return node_to_str(self.ast, "")
