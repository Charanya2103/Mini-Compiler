import sys
import argparse

# Import all of our specialized compilation phases
from lexer import tokenize
from parser import parse_tokens
from parser_nodes import *
from semantic_analyzer import analyze_semantics
from tac_generator import generate_tac, IntermediateInstruction
from optimizer import optimize_instructions
from code_generator import generate_assembly
from executor import execute_program

def _sep(title, width=60):
    """Helper function to print a clean visual separator line for the terminal."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print('=' * width)

def print_ast(node, indent=0):
    """
    A recursive helper function to print out the AST tree structure visually.
    It adds spaces (indentation) to show nested relationships.
    """
    pad = '  ' * indent
    if isinstance(node, ProgramNode):
        print(f"{pad}Program")
        for statement in node.statements: 
            print_ast(statement, indent + 1)
    elif isinstance(node, AssignNode):
        print(f"{pad}Assign -> {node.name}")
        print_ast(node.expr, indent + 1)
    elif isinstance(node, PrintNode):
        print(f"{pad}Print")
        print_ast(node.expr, indent + 1)
    elif isinstance(node, InputNode):
        print(f"{pad}Input -> {node.name}")
    elif isinstance(node, IfNode):
        print(f"{pad}If")
        print(f"{pad}  cond:"); print_ast(node.cond, indent + 2)
        print(f"{pad}  then:")
        for statement in node.then_body: 
            print_ast(statement, indent + 2)
        if node.else_body:
            print(f"{pad}  else:")
            for statement in node.else_body: 
                print_ast(statement, indent + 2)
    elif isinstance(node, WhileNode):
        print(f"{pad}While")
        print(f"{pad}  cond:"); print_ast(node.cond, indent + 2)
        print(f"{pad}  body:")
        for statement in node.body: 
            print_ast(statement, indent + 2)
    elif isinstance(node, ForNode):
        print(f"{pad}For {node.var_name} from:")
        print_ast(node.start_expr, indent + 2)
        print(f"{pad}to:")
        print_ast(node.end_expr, indent + 2)
        print(f"{pad}body:")
        for statement in node.body:
            print_ast(statement, indent + 2)
    elif isinstance(node, BinOpNode) or isinstance(node, LogicalOpNode):
        print(f"{pad}Op({node.op})")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, VarNode):
        print(f"{pad}Var({node.name})")
    elif isinstance(node, NumNode) or isinstance(node, FloatNode):
        print(f"{pad}Num({node.value})")
    elif isinstance(node, StringNode):
        print(f"{pad}Str(\"{node.value}\")")

def print_tac(instructions):
    """Prints our Three-Address Code instructions in Quadruple Notation."""
    print(f"    {'OP':<8} | {'ARG1':<10} | {'ARG2':<10} | {'RESULT':<10}")
    print(f"    {'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")
    for instr in instructions:
        # Replace 'None' with an empty string for a cleaner table
        op = str(instr.op) if instr.op else ''
        arg1 = str(instr.arg1) if instr.arg1 else ''
        arg2 = str(instr.arg2) if instr.arg2 else ''
        result = str(instr.result) if instr.result else ''
        print(f"    {op:<8} | {arg1:<10} | {arg2:<10} | {result:<10}")

def print_asm(lines):
    """Prints our Assembly code, indenting standard lines but keeping labels left-aligned."""
    for line in lines:
        prefix = '' if line.startswith('LABEL') else '      '
        print(f"    {prefix}{line}")

def compile_and_run(source):
    """
    The main driver function! This passes the source code through 
    all 7 phases of our compiler pipeline sequentially.
    """
    # Phase 1: Lexing (Source Code -> Tokens)
    _sep("PHASE 1 — TOKENS")
    tokens = tokenize(source)
    
    # Print the tokens in a clean, readable table format
    print(f"  {'TYPE':<12} | {'VALUE':<20} | {'POSITION':<8}")
    print(f"  {'-'*12}-+-{'-'*20}-+-{'-'*8}")
    for token in tokens:
        print(f"  {token.type:<12} | {token.value:<20} | {token.pos:<8}")

    # Phase 2: Parsing (Tokens -> AST Tree)
    _sep("PHASE 2 — ABSTRACT SYNTAX TREE")
    ast = parse_tokens(tokens)
    print_ast(ast) # Show the generated tree structure

    # Phase 3: Semantic Analysis (Checking for Logic Errors)
    _sep("PHASE 3 — SEMANTIC ANALYSIS")
    symbol_table = analyze_semantics(ast)
    print("  Symbol Table:")
    for name, data_type in symbol_table.items():
        print(f"    {name:>12}  ->  {data_type}")
    print("\n  [OK] All variables defined before use.")

    # Phase 4: TAC Generation (AST -> Flat TAC Code)
    _sep("PHASE 4 — THREE-ADDRESS CODE (TAC)")
    raw_tac = generate_tac(ast)
    print_tac(raw_tac)

    # Phase 5: Optimization (Speeding up TAC Code)
    _sep("PHASE 5 — OPTIMIZED TAC")
    optimized_tac = optimize_instructions(raw_tac)
    print_tac(optimized_tac)

    # Phase 6: Target Code (Optimized TAC -> Assembly Code)
    _sep("PHASE 6 — TARGET ASSEMBLY CODE")
    assembly_lines = generate_assembly(optimized_tac)
    print_asm(assembly_lines)

    # Phase 7: Execution (Running the original AST using our Interpreter)
    _sep("PHASE 7 — PROGRAM EXECUTION OUTPUT")
        
    output = execute_program(ast)
    
    if not output:
        print("  (no output)")

# This block ensures that we only run the code if the user calls `python main.py`
if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as f:
                source_code = f.read()
            
            print(f"\n  Source: {sys.argv[1]}")
            # Send the file contents into our compiler!
            compile_and_run(source_code)
            sys.exit(0)
        except FileNotFoundError:
            print(f"Error: Could not find file '{sys.argv[1]}'")
            sys.exit(1)
    else:
        # Tell the user how to use the program if they forgot the filename
        print("Usage: python main.py <source_file>")
        sys.exit(1)
