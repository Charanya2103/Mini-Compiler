# ==========================================
# ABSTRACT SYNTAX TREE (AST) NODES
# ==========================================
# These classes define the shape of our Abstract Syntax Tree.
# An AST is a branching tree structure that represents the logical flow of the code.
# Instead of a flat list of tokens, the code is organized into "Statements" and "Expressions".

class ProgramNode:
    """The root of the entire program, containing a list of all statements to execute."""
    def __init__(self, statements):
        self.statements = statements

class AssignNode:
    """Represents assigning a value to a variable (e.g., SET x TO 5)"""
    def __init__(self, name, expr):
        self.name = name # The name of the variable (e.g., 'x')
        self.expr = expr # The expression representing the value (e.g., 5)

class PrintNode:
    """Represents a command to print something to the screen."""
    def __init__(self, expr):
        self.expr = expr # What we want to print

class InputNode:
    """Represents asking the user to type in a value for a variable."""
    def __init__(self, name):
        self.name = name # The variable where the user's input will be stored

class IfNode:
    """Represents an IF/THEN/ELSE conditional block."""
    def __init__(self, cond, then_body, else_body):
        self.cond = cond           # The condition to evaluate (e.g., x > 5)
        self.then_body = then_body # The statements to run if true
        self.else_body = else_body # The statements to run if false

class WhileNode:
    """Represents a WHILE loop that repeats as long as a condition is true."""
    def __init__(self, cond, body):
        self.cond = cond # The condition to check before each loop
        self.body = body # The statements to execute inside the loop

class ForNode:
    """Represents a FOR loop that counts from a start value to an end value."""
    def __init__(self, var_name, start_expr, end_expr, body):
        self.var_name = var_name     # The counter variable (e.g., 'i')
        self.start_expr = start_expr # The starting number
        self.end_expr = end_expr     # The ending number
        self.body = body             # The statements to execute

class BinOpNode:
    """Represents a Binary Operation (math or comparison with two sides: left + right)."""
    def __init__(self, op, left, right):
        self.op = op       # The operator (e.g., '+', '*', '<')
        self.left = left   # The left side of the equation
        self.right = right # The right side of the equation

class LogicalOpNode:
    """Represents logical AND / OR operations."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class NumNode:
    """Represents a literal integer number."""
    def __init__(self, value):
        self.value = value

class FloatNode:
    """Represents a literal decimal number."""
    def __init__(self, value):
        self.value = value

class StringNode:
    """Represents a literal text string."""
    def __init__(self, value):
        self.value = value

class VarNode:
    """Represents the usage of a variable in an expression (e.g., x + 2)."""
    def __init__(self, name):
        self.name = name
