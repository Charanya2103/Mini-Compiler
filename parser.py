from lexer import Token
from parser_nodes import *

# ==========================================
# PHASE 2: SYNTAX ANALYSIS (THE PARSER)
# ==========================================
# The Parser takes the flat list of Tokens from the Lexer and organizes them 
# into a logical Abstract Syntax Tree (AST). It does this by checking the grammar 
# rules of our language (e.g., IF must be followed by a condition, then THEN).
# This specific type of parser is called a "Recursive-Descent Parser".

def parse_tokens(tokens):
    """Converts a list of Tokens into a hierarchical AST."""
    
    # We use a dictionary to track our current position in the token list.
    # We do this instead of a simple integer so that helper functions can update it.
    state = {'pos': 0}

    def current():
        """Returns the token we are currently looking at, or None if we are at the end."""
        if state['pos'] < len(tokens):
            return tokens[state['pos']]
        return None

    def consume(expected_type, expected_value=None):
        """
        Checks if the current token matches what we expect.
        If it matches, we move forward. If not, we throw a SyntaxError.
        """
        token = current()
        
        # First check if the token type matches (e.g., is it a KEYWORD?)
        if token is None or token.type != expected_type:
            got = repr(token) if token else 'EOF' # EOF means End Of File
            raise SyntaxError(f"Expected {expected_type} but got {got}")
            
        # Then check if the specific value matches (e.g., is the KEYWORD 'SET'?)
        if expected_value is not None and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}' but got '{token.value}'")
            
        # If it matched, advance our position to the next token
        state['pos'] += 1
        return token

    def match(expected_type, *expected_values):
        """
        Checks if the current token matches what we expect, but DOES NOT throw an error 
        or move forward if it fails. It just returns True or False. Used for peeking.
        """
        token = current()
        if token is None or token.type != expected_type:
            return False
        if not expected_values:
            return True # If they only checked the type, return True
        return token.value in expected_values # Check if value matches any allowed values

    # --- STATEMENT PARSING ---
    # A statement is a complete line of code (like assigning a variable or printing).

    def parse_statement():
        """Looks at the first token of a line to figure out what kind of statement it is."""
        token = current()
        if token is None:
            raise SyntaxError("Unexpected end of input")
            
        if token.type == 'KEYWORD':
            # Route to the correct parsing function based on the keyword
            if token.value == 'SET': return parse_assign()
            elif token.value == 'PRINT': return parse_print()
            elif token.value == 'IF': return parse_if()
            elif token.value == 'WHILE': return parse_while()
            elif token.value == 'FOR': return parse_for()
            elif token.value == 'INPUT': return parse_input()
            
        raise SyntaxError(f"Unknown statement starting with {token}")

    def parse_assign():
        """Parses a variable assignment: SET <var> TO <expr>"""
        consume('KEYWORD', 'SET')               # Expect the word SET
        variable_name = consume('IDENT').value  # Expect a variable name
        consume('KEYWORD', 'TO')                # Expect the word TO
        expression = parse_expr()               # Expect a mathematical/logical expression
        return AssignNode(variable_name, expression)

    def parse_print():
        """Parses a print statement: PRINT <expr>"""
        consume('KEYWORD', 'PRINT')
        expression = parse_expr()
        return PrintNode(expression)

    def parse_input():
        """Parses an input statement: INPUT <var>"""
        consume('KEYWORD', 'INPUT')
        variable_name = consume('IDENT').value
        return InputNode(variable_name)

    def parse_if():
        """Parses an IF block: IF <cond> THEN BEGIN <block> END"""
        consume('KEYWORD', 'IF')
        condition = parse_expr()
        consume('KEYWORD', 'THEN')
        consume('KEYWORD', 'BEGIN')
        then_body = parse_block() # Parse all statements inside the block
        consume('KEYWORD', 'END')
        
        else_body = []
        # Check if there is an optional ELSE block attached
        if match('KEYWORD', 'ELSE'):
            consume('KEYWORD', 'ELSE')
            consume('KEYWORD', 'BEGIN')
            else_body = parse_block()
            consume('KEYWORD', 'END')
            
        return IfNode(condition, then_body, else_body)

    def parse_while():
        """Parses a WHILE loop: WHILE <cond> DO BEGIN <block> END"""
        consume('KEYWORD', 'WHILE')
        condition = parse_expr()
        consume('KEYWORD', 'DO')
        consume('KEYWORD', 'BEGIN')
        body = parse_block()
        consume('KEYWORD', 'END')
        return WhileNode(condition, body)

    def parse_for():
        """Parses a FOR loop: FOR <var> FROM <start> TO <end> DO BEGIN <block> END"""
        consume('KEYWORD', 'FOR')
        var_name = consume('IDENT').value
        consume('KEYWORD', 'FROM')
        start_expr = parse_expr()
        consume('KEYWORD', 'TO')
        end_expr = parse_expr()
        consume('KEYWORD', 'DO')
        consume('KEYWORD', 'BEGIN')
        body = parse_block()
        consume('KEYWORD', 'END')
        return ForNode(var_name, start_expr, end_expr, body)

    def parse_block():
        """Parses multiple statements until it hits an 'END' keyword."""
        statements = []
        while current() is not None and not match('KEYWORD', 'END'):
            statements.append(parse_statement())
        return statements

    # --- EXPRESSION PARSING ---
    # Expressions are math or logic (like 5 + 5). 
    # We use multiple functions that call each other to enforce "Order of Operations" (PEMDAS).
    # The lowest priority operations (AND/OR) are at the top, and the highest priority (Numbers/Variables) are at the bottom.

    def parse_expr():
        return parse_logical()

    def parse_logical():
        """Lowest priority: AND / OR"""
        left_side = parse_comparison()
        while match('KEYWORD', 'AND', 'OR'):
            operator = current().value
            state['pos'] += 1 # Consume operator
            right_side = parse_comparison()
            left_side = LogicalOpNode(operator, left_side, right_side)
        return left_side

    def parse_comparison():
        """Priority 2: <, >, ==, !="""
        left_side = parse_arith()
        if match('OP', '<', '>', '==', '!=', '<=', '>='):
            operator = current().value
            state['pos'] += 1
            right_side = parse_arith()
            return BinOpNode(operator, left_side, right_side)
        return left_side

    def parse_arith():
        """Priority 3: +, -"""
        node = parse_term()
        while match('OP', '+', '-'):
            operator = current().value
            state['pos'] += 1
            right_side = parse_term()
            node = BinOpNode(operator, node, right_side)
        return node

    def parse_term():
        """Priority 4: *, /, %"""
        node = parse_power()
        while match('OP', '*', '/', '%'):
            operator = current().value
            state['pos'] += 1
            right_side = parse_power()
            node = BinOpNode(operator, node, right_side)
        return node

    def parse_power():
        """Priority 5: ^ (Exponents)"""
        node = parse_factor()
        # Power is usually right-associative, but for simplicity here we evaluate left-to-right
        while match('OP', '^'):
            operator = current().value
            state['pos'] += 1
            right_side = parse_factor()
            node = BinOpNode(operator, node, right_side)
        return node

    def parse_factor():
        """Highest priority: Raw numbers, strings, and variables."""
        token = current()
        if token is None:
            raise SyntaxError("Unexpected end of expression")
            
        if token.type == 'NUMBER':
            state['pos'] += 1
            return NumNode(int(token.value)) # Convert the string "5" into an actual integer 5
        elif token.type == 'FLOAT':
            state['pos'] += 1
            return FloatNode(float(token.value)) # Convert the string "3.14" into a float
        elif token.type == 'STRING':
            state['pos'] += 1
            return StringNode(token.value.strip('"')) # Remove the quote marks around the string
        elif token.type == 'IDENT':
            state['pos'] += 1
            return VarNode(token.value) # Returns the variable name
            
        raise SyntaxError(f"Unexpected token in expression: {token}")

    # --- START PARSING ---
    # Read statements continuously until the file ends.
    statements = []
    while current() is not None:
        statements.append(parse_statement())
    
    # Wrap all the statements in a root Program node
    return ProgramNode(statements)
