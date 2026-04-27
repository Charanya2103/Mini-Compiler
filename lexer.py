import re

# ==========================================
# PHASE 1: LEXICAL ANALYSIS (THE LEXER)
# ==========================================
# The Lexer's job is to take raw source code (a giant string of text) 
# and break it down into meaningful "Tokens" (like words in a sentence).
# It groups characters together and throws away useless things like spaces.

# 1. Standard Lists for Keywords and Operators
# These are the reserved words in our language that have special meaning.
KEYWORDS = [
    'SET', 'TO', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'FROM', 
    'BEGIN', 'END', 'PRINT', 'INPUT', 'AND', 'OR'
]

# These are the mathematical and logical operators.
# We sort them by length (longest first) so that a two-character operator 
# like '==' is checked before a single-character operator like '='.
OPERATORS = sorted(['!=', '==', '<=', '>=', '<', '>', '+', '-', '*', '/', '%', '^'], key=len, reverse=True)

# Build our Token Rules
# This list will hold tuples of (TokenName, RegularExpressionPattern)
TOKEN_RULES = []

# Keywords
# \b means "word boundary", ensuring we match exactly the word and not a piece of another word.
for kw in KEYWORDS:
    TOKEN_RULES.append(('KEYWORD', rf'\b{kw}\b'))

# Literals (Data values)
# \d+ means one or more digits. \. means a literal dot.
TOKEN_RULES.append(('FLOAT', r'\b\d+\.\d+\b'))
TOKEN_RULES.append(('NUMBER', r'\b\d+\b'))
# Matches anything inside double quotes.
TOKEN_RULES.append(('STRING', r'"[^"]*"'))

# Identifiers (Variable names)
# Must start with a letter [a-zA-Z], followed by zero or more letters or numbers [a-zA-Z0-9]*
TOKEN_RULES.append(('IDENT', r'\b[a-zA-Z][a-zA-Z0-9]*\b'))

# Operators
# We use re.escape to ensure symbols like '+' and '*' are treated as literal characters, 
# not as special regex commands.
for op in OPERATORS:
    TOKEN_RULES.append(('OP', re.escape(op)))

# Ignore rules
# #.* means match a hash and everything after it until the end of the line.
TOKEN_RULES.append(('COMMENT', r'#.*'))
# Match spaces, tabs, and newlines so we can skip them.
TOKEN_RULES.append(('SKIP', r'[ \t\r\n]+'))

class Token:
    """
    Represents a single meaningful word or symbol in the source code.
    Example: Token(type='KEYWORD', value='SET', pos=0)
    """
    def __init__(self, type, value, pos):
        self.type = type   # The category of the token (e.g., IDENT, NUMBER)
        self.value = value # The actual text matched (e.g., 'myVar', '5')
        self.pos = pos     # Where in the file this token was found

    def __repr__(self):
        """This function just makes debugging easier by printing tokens cleanly."""
        if self.type == 'IDENT': return f'ID({self.value})'
        if self.type == 'NUMBER': return f'NUM({self.value})'
        if self.type == 'FLOAT': return f'FLOAT({self.value})'
        if self.type == 'STRING': return f'STR({self.value})'
        if self.type == 'KEYWORD': return f'KW({self.value})'
        if self.type == 'OP': return f'OP({self.value})'
        return self.type

def tokenize(source):
    """
    Convert raw FlowLang source text into a flat list of Tokens using a list-based scanner.
    """
    tokens = []
    pos = 0 # Our current position reading through the source code text
    length = len(source)
    
    # Compile the regular expressions before we loop for speed.
    # re.IGNORECASE allows our keywords to be case-insensitive (e.g., 'set' matches 'SET').
    compiled_rules = [(name, re.compile(pattern, re.IGNORECASE)) for name, pattern in TOKEN_RULES]

    # Keep reading until we reach the end of the file
    while pos < length:
        match_found = False
        
        # Check our current position against every rule in our list, one by one.
        for token_type, regex in compiled_rules:
            # Try to find a match starting exactly at 'pos'
            match = regex.match(source, pos)
            
            if match:
                value = match.group() # Get the actual text that matched
                
                # If it's a space or a comment, we do nothing and just skip it
                if token_type not in ('SKIP', 'COMMENT'):
                    # Force keywords to always be uppercase so the Parser easily recognizes them
                    if token_type == 'KEYWORD':
                        value = value.upper()
                        
                    # Add the valid token to our final list
                    tokens.append(Token(token_type, value, pos))
                
                # Move our reading position forward by the length of the matched word
                pos = match.end()
                match_found = True
                break # We found a match, so stop checking rules and move to the next word
        
        # If we checked every single rule and nothing matched, it's an invalid character!
        if not match_found:
            raise SyntaxError(f"Illegal character '{source[pos]}' at position {pos}")

    return tokens
