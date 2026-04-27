from parser_nodes import *

# ==========================================
# PHASE 7: EXECUTION (INTERPRETER)
# ==========================================
# While a true Compiler saves the Assembly code to an .exe file to run later,
# an Interpreter runs the code immediately!
# This is a "Tree-Walking Interpreter". It takes the AST generated in Phase 2
# and literally "walks" through the tree, doing exactly what the nodes say to do.

def execute_program(ast):
    """
    Starts at the root of the AST and executes every statement.
    Returns a list of all strings that were printed so we can test it.
    """
    # The 'environment' is our memory bank. 
    # It is a simple dictionary that stores variable names and their current values.
    # E.g., {'x': 5, 'name': 'John'}
    environment = {}
    
    # A list to store everything the user PRINTS.
    output = []
    
    # Go through every statement in the main program and execute it!
    for statement in ast.statements:
        _exec_stmt(statement, environment, output)
        
    return output

def _exec_stmt(node, environment, output):
    """
    Executes a single statement (a complete action like assigning or printing).
    """
    if isinstance(node, AssignNode):
        # Calculate the value on the right, and save it in our memory dictionary!
        environment[node.name] = _eval_expr(node.expr, environment)

    elif isinstance(node, PrintNode):
        # Calculate what needs to be printed, add it to our list, and print to the screen.
        value = _eval_expr(node.expr, environment)
        output.append(str(value))
        print(value)
        
    elif isinstance(node, InputNode):
        # Use Python's built-in input() function to ask the user for data
        user_input = input(f"Enter value for {node.name}: ")
        try:
            # Try to convert their input into a Float or Integer so we can do math on it
            if '.' in user_input:
                val = float(user_input)
            else:
                val = int(user_input)
        except ValueError:
            # If it's not a number, just leave it as a String text
            val = user_input 
            
        # Save the input to memory
        environment[node.name] = val

    elif isinstance(node, IfNode):
        # First, check if the condition is True
        if _eval_expr(node.cond, environment):
            # If True, execute all statements in the THEN block
            for statement in node.then_body: 
                _exec_stmt(statement, environment, output)
        else:
            # If False, execute all statements in the ELSE block
            for statement in node.else_body: 
                _exec_stmt(statement, environment, output)

    elif isinstance(node, WhileNode):
        # While the condition is True, keep looping!
        while _eval_expr(node.cond, environment):
            # Execute every statement in the loop body
            for statement in node.body: 
                _exec_stmt(statement, environment, output)
                
    elif isinstance(node, ForNode):
        # First calculate the starting and ending numbers
        start_val = _eval_expr(node.start_expr, environment)
        end_val = _eval_expr(node.end_expr, environment)
        
        # Set the loop counter variable in memory (e.g., i = 1)
        environment[node.var_name] = start_val
        
        # Keep looping until our counter is larger than our end target
        while environment[node.var_name] <= end_val:
            # Execute the loop body
            for statement in node.body:
                _exec_stmt(statement, environment, output)
            
            # Add 1 to our counter variable automatically!
            environment[node.var_name] += 1

def _eval_expr(node, environment):
    """
    Evaluates an expression (math or logic) and returns its final computed value.
    """
    # Base cases: If it's just a raw number or string, return it directly.
    if isinstance(node, NumNode) or isinstance(node, FloatNode) or isinstance(node, StringNode):
        return node.value

    # If it's a variable, look up its current value in our memory dictionary.
    if isinstance(node, VarNode):
        if node.name not in environment:
            raise NameError(f"Undefined variable: {node.name}")
        return environment[node.name]

    # If it's a binary operation (e.g., 5 + 3)
    if isinstance(node, BinOpNode) or isinstance(node, LogicalOpNode):
        # Recursively calculate the final value of the left and right sides
        left_value = _eval_expr(node.left, environment)
        right_value = _eval_expr(node.right, environment)
        
        # String concatenation (combining text like "Hello " + "World")
        if node.op == '+' and (isinstance(left_value, str) or isinstance(right_value, str)):
            return str(left_value) + str(right_value)
        
        # Standard Math Operations
        if node.op == '+': return left_value + right_value
        elif node.op == '-': return left_value - right_value
        elif node.op == '*': return left_value * right_value
        elif node.op == '/': return left_value / right_value
        elif node.op == '%': return left_value % right_value
        elif node.op == '^': return left_value ** right_value
        
        # Standard Logical Comparisons (returns 1 for True, 0 for False)
        elif node.op == '<': return 1 if left_value < right_value else 0
        elif node.op == '>': return 1 if left_value > right_value else 0
        elif node.op == '<=': return 1 if left_value <= right_value else 0
        elif node.op == '==': return 1 if left_value == right_value else 0
        elif node.op == '!=': return 1 if left_value != right_value else 0
        
        # AND/OR Logic
        elif node.op == 'AND': return 1 if (left_value and right_value) else 0
        elif node.op == 'OR': return 1 if (left_value or right_value) else 0

    # If we don't recognize the node type, something went wrong in the AST parser!
    raise ValueError(f"Unknown node: {node}")
