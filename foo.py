#!/bin/env python

from lib.analysis.analyzer import Analyzer
from lib.nodes.class_node import ClassNode
from lib.nodes.function_node import FunctionNode

code = open('u3l23_01.js', 'r').read()
code = open('simple.js', 'r').read()
a = Analyzer(code)
math = open('math.js', 'r').read()
a.augment(math)
precode = open('precode.js', 'r').read()
a.augment(precode)

print(a)
context = a.annotate()
print("Possible values for 'player':")
variable = context.lookup('player')
if variable:
  for value in variable.get_value().values:
    if value[0] == 'reference':
      print('ref:', value[1])
a.augment("""
  function keyWentDown(key) {
    if (key === "right") { return true; }
    return false;
  }
""")
context = a.annotate()
print()
print("Context:")
print(context)
print()

print("Possible values for 'x':")
variable = context.lookup('x')
if variable:
  for value in variable.get_value().values:
    print(value[1])
print()

print("Possible values for 'player':")
variable = context.lookup('player')
if variable:
  for value in variable.get_value().values:
    if value[0] == 'reference':
      print('ref:', value[1])

import os, sys
sys.exit(0)

def count(type):
  item = context.lookup(type)
  if isinstance(item, FunctionNode):
    return context.lookup(type).called
  elif isinstance(item, ClassNode):
    return context.lookup(type).instanced
  return 0

def _assert(actual, op, expected):
  print(actual)
  assert(eval(str(actual) + ' ' + op + ' ' + str(expected)))

_assert(count('Sprite'), '>=', 2)
_assert(count('createSprite'), '>=', 2)
