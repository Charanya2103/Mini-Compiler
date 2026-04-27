from tac_generator import IntermediateInstruction

# ==========================================
# PHASE 5: OPTIMIZATION
# ==========================================
# Optimization makes the code run faster. It looks at the Three-Address Code (TAC)
# generated in Phase 4 and tries to find shortcuts to eliminate unnecessary steps.

def parse_number(s):
    """Helper function to safely try to convert a string to an integer or float."""
    try: return int(s)
    except ValueError:
        try: return float(s)
        except ValueError:
            return None

def is_string(s):
    """Checks if a value is surrounded by quotes."""
    return s and s.startswith('"') and s.endswith('"')

def constant_fold(instructions):
    """
    Constant Folding optimization:
    If the compiler sees math using only constants (e.g., t1 = 3 + 4), 
    it evaluates the math RIGHT NOW (t1 = 7). This saves the final program 
    from having to compute it every time it runs!
    """
    optimized_instructions = []
    for instruction in instructions:
        # Check if this instruction is a math operation
        if instruction.arg1 and instruction.arg2 and instruction.op in ('+', '-', '*', '/', '%', '^', 'AND', 'OR'):
            val1 = parse_number(instruction.arg1)
            val2 = parse_number(instruction.arg2)
            
            # String concatenation optimization (e.g., "Hello " + "World")
            if instruction.op == '+' and is_string(instruction.arg1) and is_string(instruction.arg2):
                str1 = instruction.arg1.strip('"')
                str2 = instruction.arg2.strip('"')
                optimized_instructions.append(IntermediateInstruction('=', instruction.result, f'"{str1}{str2}"'))
                continue

            # If both arguments are actual numbers, we can do the math now!
            if val1 is not None and val2 is not None:
                if instruction.op == '+': folded_value = val1 + val2
                elif instruction.op == '-': folded_value = val1 - val2
                elif instruction.op == '*': folded_value = val1 * val2
                elif instruction.op == '/': folded_value = val1 / val2
                elif instruction.op == '%': folded_value = val1 % val2
                elif instruction.op == '^': folded_value = val1 ** val2
                elif instruction.op == 'AND': folded_value = 1 if (val1 and val2) else 0
                elif instruction.op == 'OR': folded_value = 1 if (val1 or val2) else 0
                else: folded_value = 0
                
                # Replace the math instruction with a simple assignment (t1 = 7)
                optimized_instructions.append(IntermediateInstruction('=', instruction.result, str(folded_value)))
            else:
                optimized_instructions.append(instruction)
        else:
            optimized_instructions.append(instruction)
            
    return optimized_instructions

def eliminate_dead_copies(instructions):
    """
    Dead-Copy Elimination optimization:
    Sometimes the TAC generator creates useless middle-men.
    Example: 
        t1 = 5 
        x = t1
    If `t1` is never used again, we can just rewrite this as `x = 5` and delete `t1` entirely!
    """
    # Step 1: Count how many times each temp variable is used
    use_count = {}
    for instruction in instructions:
        for field in (instruction.arg1, instruction.arg2):
            if field and field.startswith('t') and field[1:].isdigit():
                use_count[field] = use_count.get(field, 0) + 1

    # Step 2: Build a map of temps that are just copied and only used once
    substitution_map = {}
    for instruction in instructions:
        # Check if this is a direct assignment:  real_variable = temp_variable
        # We must make sure the 'real_variable' isn't ALSO a temporary variable (like t1, t2).
        # Previously we just checked if it started with 't', which accidentally excluded "total"!
        is_result_temp = instruction.result and instruction.result.startswith('t') and instruction.result[1:].isdigit()
        is_arg_temp = instruction.arg1 and instruction.arg1.startswith('t') and instruction.arg1[1:].isdigit()
        
        if (instruction.op == '='
                and instruction.result and not is_result_temp
                and is_arg_temp
                and use_count.get(instruction.arg1, 0) == 1):
            
            # Remember that we want to replace 'temp_variable' with 'real_variable'
            substitution_map[instruction.arg1] = instruction.result

    # Step 3: Apply the substitutions and remove the redundant instructions
    new_instructions = []
    for instruction in instructions:
        # Skip adding the redundant copy instruction itself
        if instruction.op == '=' and instruction.arg1 in substitution_map:
            continue
            
        # Replace the temp variable with the real variable everywhere it appears
        new_arg1 = substitution_map.get(instruction.arg1, instruction.arg1)
        new_arg2 = substitution_map.get(instruction.arg2, instruction.arg2)
        new_result = substitution_map.get(instruction.result, instruction.result)
        
        new_instructions.append(IntermediateInstruction(instruction.op, new_result, new_arg1, new_arg2))

    return new_instructions

def optimize_instructions(instructions):
    """
    Applies all of our optimization techniques to the intermediate code to speed it up.
    """
    instructions = constant_fold(instructions)
    instructions = eliminate_dead_copies(instructions)
    return instructions
