"""This is a reusable Python module intended to store
my accumulated Python knowledge"""

from pprint import pprint


CONCEPTS = dict(
  keywords='reserved words in Python you cannot use as variable names', 
  variables=r'names in Python that point to objects - [A-Za-z_][\w]*',
  arity='number of arguments a function takes: nullary, unary, binary, ternary',  docstrings='strings at the tope of a module , class or function definition that document the code',
  comments=' # (the octothorpe) - and anything that follows it',
  naming="name your objects so well you don't need comments",

  )

def main():
    """pretty prints the data in this module"""
    pprint(CONCEPTS)

if __name__ == '__main__':
    main()
