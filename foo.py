#!/bin/env python

from lib.analysis.analyzer import Analyzer

code = open('u3l23_01.js', 'r').read()
code = open('simple.js', 'r').read()
a = Analyzer(code)
math = open('math.js', 'r').read()
a.augment(math)
precode = open('precode.js', 'r').read()
a.augment(precode)
print(a)
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
print(variable)
if variable:
  for value in variable.get_value().values:
    if value[0] == 'reference':
      print(value[1])
