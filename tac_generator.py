from typing import Optional
from parser_nodes import *

# ==========================================
# PHASE 4: THREE-ADDRESS CODE (TAC) GENERATION
# ==========================================
# Computers are bad at dealing with deeply nested trees (like our AST).
# They prefer a flat, linear list of instructions.
# Three-Address Code (TAC) is a generic intermediate step. It breaks complex math
# like `x = (1 + 2) * (3 + 4)` into simple, bite-sized instructions:
#   t1 = 1 + 2
#   t2 = 3 + 4
#   x = t1 * t2

class IntermediateInstruction:
    """
    A single linear instruction. It's called 'Three-Address' because it
    usually has up to 3 parts: a result, an argument 1, and an argument 2.
    Example: result = arg1 + arg2
    """
    def __init__(self, op, result=None, arg1=None, arg2=None):
        self.op = op         # The operation (+, -, GOTO, LABEL)
        self.result = result # Where to store the answer (e.g., 't1', 'x')
        self.arg1 = arg1     # The first variable/number
        self.arg2 = arg2     # The second variable/number

    def __repr__(self):
        """Format the instruction to look like clean code for debugging."""
        if self.op == 'LABEL': return f'{self.result}:'
        if self.op == 'GOTO': return f'GOTO {self.result}'
        if self.op == 'JZ': return f'IF FALSE {self.arg1} GOTO {self.result}'
        if self.op == 'PRINT': return f'PRINT {self.arg1}'
        if self.op == 'INPUT': return f'INPUT {self.arg1}'
        if self.arg2: return f'{self.result} = {self.arg1} {self.op} {self.arg2}'
        if self.arg1: return f'{self.result} = {self.arg1}'
        return f'{self.op} {self.result}'

def generate_tac(ast):
    """Generates a linear list of Intermediate Instructions from the AST."""
    instructions = []
    
    # We use a dictionary to keep track of our counters so our helper functions can update them.
    # We need to generate unique names for Temporary Variables (t1, t2) and Jump Labels (L1, L2).
    state = {'temp_count': 0, 'label_count': 0}

    def new_temp():
        """Creates a new unique temporary variable (e.g., 't1', 't2')"""
        state['temp_count'] += 1
        return f"t{state['temp_count']}"

    def new_label():
        """Creates a new unique jump label for loops/if statements (e.g., 'L1', 'L2')"""
        state['label_count'] += 1
        return f"L{state['label_count']}"

    def emit(instruction):
        """Adds a new instruction to our final list."""
        instructions.append(instruction)

    def gen_stmt(node):
        """Generates TAC for a statement."""
        if isinstance(node, AssignNode):
            # First, simplify the math expression into a single temporary variable
            value = gen_expr(node.expr)
            # Then, assign that temporary variable to our real variable
            emit(IntermediateInstruction('=', node.name, value))

        elif isinstance(node, PrintNode):
            value = gen_expr(node.expr)
            emit(IntermediateInstruction('PRINT', arg1=value))

        elif isinstance(node, InputNode):
            emit(IntermediateInstruction('INPUT', arg1=node.name))

        elif isinstance(node, IfNode):
            # Flatten the condition into a true/false variable
            cond_result = gen_condition(node.cond)
            else_label = new_label()
            end_label = new_label()
            
            # 'JZ' stands for 'Jump if Zero'. If the condition is false (0), jump to the ELSE block.
            emit(IntermediateInstruction('JZ', result=else_label, arg1=cond_result))
            
            # Generate the code for the THEN block
            for statement in node.then_body:
                gen_stmt(statement)
            # After the THEN block finishes, jump over the ELSE block to the end.
            emit(IntermediateInstruction('GOTO', result=end_label))
            
            # Place the ELSE label here
            emit(IntermediateInstruction('LABEL', result=else_label))
            for statement in node.else_body:
                gen_stmt(statement)
            
            # Place the END label here
            emit(IntermediateInstruction('LABEL', result=end_label))

        elif isinstance(node, WhileNode):
            start_label = new_label()
            end_label = new_label()
            
            # Place a label at the very start so we can loop back here
            emit(IntermediateInstruction('LABEL', result=start_label))
            cond_result = gen_condition(node.cond)
            
            # If the condition is false, jump to the end (break the loop)
            emit(IntermediateInstruction('JZ', result=end_label, arg1=cond_result))
            
            # Generate the body of the loop
            for statement in node.body:
                gen_stmt(statement)
                
            # Jump back up to the start to check the condition again!
            emit(IntermediateInstruction('GOTO', result=start_label))
            
            # Place the END label here
            emit(IntermediateInstruction('LABEL', result=end_label))

        elif isinstance(node, ForNode):
            # A FOR loop is basically a WHILE loop with automatic counting!
            start_val = gen_expr(node.start_expr)
            emit(IntermediateInstruction('=', node.var_name, start_val))
            
            start_label = new_label()
            end_label = new_label()
            emit(IntermediateInstruction('LABEL', result=start_label))
            
            end_val = gen_expr(node.end_expr)
            cond_temp = new_temp()
            # Check if variable <= end_val
            emit(IntermediateInstruction('<=', cond_temp, node.var_name, end_val))
            emit(IntermediateInstruction('JZ', result=end_label, arg1=cond_temp))
            
            for statement in node.body:
                gen_stmt(statement)
                
            # Automatically add 1 to the loop variable
            inc_temp = new_temp()
            emit(IntermediateInstruction('+', inc_temp, node.var_name, '1'))
            emit(IntermediateInstruction('=', node.var_name, inc_temp))
            
            emit(IntermediateInstruction('GOTO', result=start_label))
            emit(IntermediateInstruction('LABEL', result=end_label))

    def gen_condition(node):
        """Helper to generate comparison code."""
        if isinstance(node, BinOpNode) and node.op in ('<', '>', '==', '!=', '<='):
            left_side = gen_expr(node.left)
            right_side = gen_expr(node.right)
            temp_var = new_temp()
            emit(IntermediateInstruction(node.op, temp_var, left_side, right_side))
            return temp_var
        return gen_expr(node)

    def gen_expr(node):
        """Generates TAC for math and expressions, returning the variable name holding the answer."""
        if isinstance(node, NumNode) or isinstance(node, FloatNode):
            return str(node.value)
        if isinstance(node, StringNode):
            return f'"{node.value}"'
        if isinstance(node, VarNode):
            return node.name
        if isinstance(node, BinOpNode) or isinstance(node, LogicalOpNode):
            # Recursively break down the left and right sides
            left_side = gen_expr(node.left)
            right_side = gen_expr(node.right)
            # Create a temporary variable to hold the answer of this specific math operation
            temp_var = new_temp()
            emit(IntermediateInstruction(node.op, temp_var, left_side, right_side))
            return temp_var
            
        raise ValueError(f"Unknown AST node: {node}")

    # Start generation at the root of the AST
    for statement in ast.statements:
        gen_stmt(statement)
        
    return instructions
