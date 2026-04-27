from parser_nodes import *

# ==========================================
# PHASE 3: SEMANTIC ANALYSIS
# ==========================================
# The Semantic Analyzer walks through the AST and enforces the "rules of meaning".
# While the Parser checks if the grammar is correct (e.g., noun before verb), 
# the Semantic Analyzer checks if the sentence actually makes sense.
# Its main job in FlowLang is to make sure you never try to use a variable 
# before you have given it a value (assigned it).

def analyze_semantics(ast):
    """
    Walks the AST to enforce semantic rules.
    Returns a 'symbol table' which is a dictionary mapping variable names to their type.
    """
    # The Symbol Table remembers every variable we've seen and what type of data it holds.
    symbol_table = {}   

    def analyze(node, defined_variables=None):
        """
        A recursive function that looks at a node, checks it for errors, 
        and then calls itself to check the node's children.
        """
        # We use a 'set' to keep track of variables that currently have a value.
        if defined_variables is None:
            defined_variables = set()

        if isinstance(node, ProgramNode):
            # For the main program, just analyze every statement inside it.
            for statement in node.statements:
                analyze(statement, defined_variables)

        elif isinstance(node, AssignNode):
            # First, check the right side of the equals sign (the math/logic)
            analyze(node.expr, defined_variables)
            # Then, mark this variable as defined since it now has a value!
            defined_variables.add(node.name)
            
            # Simple Type Inference!
            # If we assign a raw number or string, we can guess the type!
            if isinstance(node.expr, NumNode):
                symbol_table[node.name] = 'int'
            elif isinstance(node.expr, FloatNode):
                symbol_table[node.name] = 'float'
            elif isinstance(node.expr, StringNode):
                symbol_table[node.name] = 'string'
            else:
                # If it's a math expression (x = a + b), we just fall back to 'any'
                symbol_table[node.name] = 'any'

        elif isinstance(node, InputNode):
            # Getting input from a user defines the variable
            defined_variables.add(node.name)
            symbol_table[node.name] = 'any'

        elif isinstance(node, PrintNode):
            # Just check the expression we are trying to print
            analyze(node.expr, defined_variables)

        elif isinstance(node, IfNode):
            # First check the condition (e.g. x > 5)
            analyze(node.cond, defined_variables)
            
            # Create a copy of the defined variables for the THEN branch.
            # Variables defined inside the THEN branch shouldn't accidentally leak out.
            branch_defined = set(defined_variables)
            for statement in node.then_body:
                analyze(statement, branch_defined)
                
            # Create another copy for the ELSE branch
            else_defined = set(defined_variables)
            for statement in node.else_body:
                analyze(statement, else_defined)
                
            # If a variable was defined in BOTH the 'then' and 'else' branch, 
            # we know for a fact it is defined going forward!
            defined_variables |= branch_defined & else_defined

        elif isinstance(node, WhileNode):
            analyze(node.cond, defined_variables)
            loop_defined = set(defined_variables)
            for statement in node.body:
                analyze(statement, loop_defined)

        elif isinstance(node, ForNode):
            analyze(node.start_expr, defined_variables)
            analyze(node.end_expr, defined_variables)
            
            loop_defined = set(defined_variables)
            # The loop variable (e.g., 'i') is officially defined inside the loop!
            loop_defined.add(node.var_name)
            symbol_table[node.var_name] = 'int'
            
            for statement in node.body:
                analyze(statement, loop_defined)

        elif isinstance(node, BinOpNode) or isinstance(node, LogicalOpNode):
            # Check both the left and right sides of the math equation
            analyze(node.left, defined_variables)
            analyze(node.right, defined_variables)

        elif isinstance(node, VarNode):
            # **THE MOST IMPORTANT CHECK**
            # If we try to use a variable, but its name is not in our list of defined variables,
            # we crash the compiler because the user made a typo or forgot to define it!
            if node.name not in defined_variables:
                raise NameError(f"Variable '{node.name}' used before assignment")

        elif isinstance(node, (NumNode, FloatNode, StringNode)):
            # Raw numbers and strings don't need semantic checking.
            pass

    # Start the analysis at the very top of the tree
    analyze(ast)
    return symbol_table
