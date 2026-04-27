from tac_generator import IntermediateInstruction

# ==========================================
# PHASE 6: TARGET CODE GENERATION
# ==========================================
# This is the final stage of translating the code. We take our optimized 
# Three-Address Code (TAC) and convert it into the final output language.
# In a real compiler, this would be Machine Code (1s and 0s) or Assembly (x86, ARM).
# For our toy language, we generate a fake, simple Stack-Based Assembly Language.

# A dictionary mapping our TAC math symbols to their Assembly equivalents.
ASMOP = {
    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', 
    '%': 'MOD', '^': 'POW', 'AND': 'AND', 'OR': 'OR'
}

def generate_assembly(instructions):
    """
    Translates optimized intermediate code (TAC) into simple assembly language lines.
    """
    assembly_lines = []

    def emit(line):
        """Helper to add a line of assembly code to our final output list."""
        assembly_lines.append(line)

    # Go through every TAC instruction one by one
    for instruction in instructions:
        op = instruction.op

        # Jump Labels (e.g., L1:)
        if op == 'LABEL':
            emit(f'LABEL {instruction.result}')

        # Unconditional Jumps
        elif op == 'GOTO':
            emit(f'JMP {instruction.result}') # Assembly usually calls jumps 'JMP'

        # Printing
        elif op == 'PRINT':
            # In Assembly, you usually LOAD a value into a register, then call PRINT
            emit(f'LOAD {instruction.arg1}')
            emit('PRINT')
            
        # Input
        elif op == 'INPUT':
            # Ask for input, then STORE it into a memory location
            emit('INPUT')
            emit(f'STORE {instruction.arg1}')

        # Assignment (x = 5)
        elif op == '=':
            # LOAD the value (5), then STORE it into memory (x)
            emit(f'LOAD {instruction.arg1}')
            emit(f'STORE {instruction.result}')

        # Basic Math (+, -, *)
        elif op in ASMOP:
            # Assembly math usually looks like:
            # LOAD first_number
            # ADD second_number
            # STORE answer
            emit(f'LOAD {instruction.arg1}')
            emit(f'{ASMOP[op]} {instruction.arg2}')
            emit(f'STORE {instruction.result}')

        # Logical Comparisons (<, >, ==)
        elif op in ('<', '>', '==', '!=', '<='):
            # Assembly comparison:
            # LOAD first_number
            # CMP second_number (Compare)
            # STORE result (1 for true, 0 for false)
            emit(f'LOAD {instruction.arg1}')
            emit(f'CMP {instruction.arg2}')
            emit(f'STORE {instruction.result}')

        # Jump if Zero (Conditional Jump for IF statements and Loops)
        elif op == 'JZ':
            # LOAD the condition result (true/false)
            # If it is 0 (false), JZ (Jump if Zero) to the target label.
            emit(f'LOAD {instruction.arg1}')
            emit(f'JZ {instruction.result}')

    return assembly_lines
