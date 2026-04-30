# Mini-Compiler
## FlowLang - Mini compiler

FlowLang is a simple, interpreted programming language that demonstrates a complete compiler pipeline. It supports:

- **Variables** - Dynamic typing with automatic type inference
- **Arithmetic** - Full mathematical operations
- **Control Flow** - IF/ELSE, WHILE, FOR loops
- **Input/Output** - PRINT and INPUT statements

**Example FlowLang Program:**
```flow
SET count TO 0
WHILE count < 5 DO BEGIN
    PRINT "Count is: " + count
    SET count TO count + 1
END
```
---

##  Features

 **Complete Compiler Pipeline** - All 7 traditional compilation phases  
 **Case-Insensitive Keywords** - Write `SET`, `set`, or `SeT`—they all work  
 **Automatic Type Inference** - Variables are automatically typed    
**Block Scoping** - Safe variable scope handling  
 **Optimization** - Constant folding and dead-copy elimination  
 **Error Reporting** - Clear, meaningful error messages  
 **Educational** - Learn how real compilers work!

---

## 🔄 The 7 Phases of Compilation

### **Phase 1: Lexical Analysis (Lexer)**
Breaks raw source code into tokens (keywords, identifiers, operators, numbers).

**Input:** Raw FlowLang code  
**Output:** Stream of tokens  
**File:** [`lexer.py`](lexer.py)

---

### **Phase 2: Syntax Analysis (Parser)**
Organizes tokens into a hierarchical Abstract Syntax Tree (AST) using grammar rules.

**Input:** Token stream  
**Output:** Abstract Syntax Tree (AST)  
**File:** [`parser.py`](parser.py)

**Parser Rules:**
- Statements: SET, PRINT, INPUT, IF/ELSE, WHILE, FOR
- Expressions: Logical → Comparison → Arithmetic → Term → Power → Factor
- Operator Precedence: Automatic enforcement via function hierarchy

---

### **Phase 3: Semantic Analysis**
Validates that the code makes logical sense (variable scope, type consistency, etc.).

**Input:** AST  
**Output:** Validated AST + Symbol Table  
**File:** [`semantic_analyzer.py`](semantic_analyzer.py)

**Checks:**
- Variable defined before use
- Type inference
- Block scoping
- No undefined variables

---

### **Phase 4: Three-Address Code Generation (TAC)**
Converts the AST into intermediate code that's closer to machine language.

**Input:** Validated AST  
**Output:** Three-Address Code (intermediate)  
**File:** [`tac_generator.py`](tac_generator.py)

**Example:**
```
SET x TO 10 + 5
```
Becomes:
```
t1 = 10 + 5
x = t1
```

---

### **Phase 5: Optimization**
Eliminates redundancy and improves performance (constant folding, dead-copy elimination).

**Input:** Three-Address Code  
**Output:** Optimized Three-Address Code  
**File:** [`optimizer.py`](optimizer.py)

**Optimizations:**
- **Constant Folding:** `t1 = 3 + 4` → `t1 = 7`
- **Dead-Copy Elimination:** `t1 = 5; x = t1` → `x = 5`

---

### **Phase 6: Target Code Generation**
Converts intermediate code to a stack-based assembly language.

**Input:** Optimized TAC  
**Output:** Assembly code  
**File:** [`code_generator.py`](code_generator.py)

**Assembly Instructions:**
- `LOAD value` - Load value onto stack
- `STORE var` - Store to memory
- `ADD`, `SUB`, `MUL`, `DIV` - Arithmetic
- `JMP`, `JZ` - Jumps for control flow

---

### **Phase 7: Execution (Interpreter)**
Actually runs the code by walking the AST and updating an environment dictionary.

**Input:** AST (or assembly from Phase 6)  
**Output:** Program output  
**File:** [`executor.py`](executor.py)

---

## 📝 Language Syntax

### Data Types
FlowLang has automatic type inference:
- **Numbers:** `5`, `100`, `-50`
- **Floats:** `3.14`, `0.5`, `-2.71`
- **Strings:** `"Hello"`, `"World"`

### Keywords
- **Control:** `SET`, `PRINT`, `INPUT`
- **Conditionals:** `IF`, `THEN`, `ELSE`, `END`
- **Loops:** `WHILE`, `FOR`, `DO`, `BEGIN`, `END`, `FROM`, `TO`
- **Logic:** `AND`, `OR`

### Operators

**Arithmetic:**
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo
- `^` Power

**Comparison:**
- `<` Less than
- `>` Greater than
- `==` Equal to
- `!=` Not equal to
- `<=` Less than or equal
- `>=` Greater than or equal

**Logical:**
- `AND` Logical AND
- `OR` Logical OR

### Statements

#### Variable Assignment
```flow
SET variable_name TO expression
```
**Example:** `SET score TO 100`

#### Print Output
```flow
PRINT expression
```
**Example:** `PRINT "Score: " + score`

#### Input
```flow
INPUT variable_name
```
**Example:** `INPUT age`

#### If/Else Statement
```flow
IF condition THEN BEGIN
    statements
END
[ELSE BEGIN
    statements
END]
```

**Example:**
```flow
IF x > 0 THEN BEGIN
    PRINT "Positive"
END
ELSE BEGIN
    PRINT "Non-positive"
END
```

#### While Loop
```flow
WHILE condition DO BEGIN
    statements
END
```

**Example:**
```flow
WHILE count < 10 DO BEGIN
    PRINT count
    SET count TO count + 1
END
```

#### For Loop
```flow
FOR variable FROM start TO end DO BEGIN
    statements
END
```

**Example:**
```flow
FOR i FROM 1 TO 5 DO BEGIN
    PRINT i
END
```
---


### File Descriptions

| File | Purpose | Phase |
|------|---------|-------|
| `lexer.py` | Tokenizes source code | 1 |
| `parser.py` | Builds AST from tokens | 2 |
| `parser_nodes.py` | Defines AST node classes | - |
| `semantic_analyzer.py` | Validates semantics | 3 |
| `tac_generator.py` | Generates intermediate code | 4 |
| `optimizer.py` | Optimizes code | 5 |
| `code_generator.py` | Generates assembly | 6 |
| `executor.py` | Executes the program | 7 |
| `main.py` | Main entry point | - |
