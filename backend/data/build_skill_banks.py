"""
Generates complete 50 MCQs + 2 Programming Questions for:
1. Python
2. SQL
3. Java
conforming to the required topic and difficulty distributions.
"""

import json
import os

def create_python_bank():
    mcqs = [
        # Basic Concepts (5)
        {"id": 1, "topic": "Basic Concepts", "difficulty": "Easy",
         "question": "Which of the following is true about Python?",
         "options": ["It is statically typed and compiled", "It is dynamically typed and interpreted", "It requires explicit memory management", "It does not support object-oriented programming"],
         "correct_option": 1, "explanation": "Python is an interpreted, high-level, dynamically typed language."},
        {"id": 2, "topic": "Basic Concepts", "difficulty": "Easy",
         "question": "What is the standard implementation of Python written in C called?",
         "options": ["PyPy", "Jython", "CPython", "IronPython"],
         "correct_option": 2, "explanation": "CPython is the reference implementation of Python written in C."},
        {"id": 3, "topic": "Basic Concepts", "difficulty": "Easy",
         "question": "Which keyword is used to define a function in Python?",
         "options": ["function", "fun", "def", "lambda"],
         "correct_option": 2, "explanation": "The 'def' keyword is used to define named functions in Python."},
        {"id": 4, "topic": "Basic Concepts", "difficulty": "Medium",
         "question": "What is PEP 8 in Python?",
         "options": ["A Python compiler enhancement", "The official style guide for Python code", "A package manager", "A virtual environment standard"],
         "correct_option": 1, "explanation": "PEP 8 is the Python Enhancement Proposal that specifies coding style conventions."},
        {"id": 5, "topic": "Basic Concepts", "difficulty": "Hard",
         "question": "What does the Global Interpreter Lock (GIL) do in CPython?",
         "options": ["Allows multiple threads to execute Python bytecodes simultaneously", "Prevents multiple native threads from executing Python bytecodes at once", "Locks all global variables against mutations", "Prevents memory leaks in garbage collection"],
         "correct_option": 1, "explanation": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes concurrently in CPython."},

        # Syntax & Comments (4)
        {"id": 6, "topic": "Syntax", "difficulty": "Easy",
         "question": "How are code blocks indicated in Python?",
         "options": ["Curly braces {}", "Indentation with whitespace", "Begin and End keywords", "Parentheses ()"],
         "correct_option": 1, "explanation": "Python uses whitespace indentation to define code blocks instead of curly braces."},
        {"id": 7, "topic": "Syntax", "difficulty": "Easy",
         "question": "Which symbol is used for single-line comments in Python?",
         "options": ["//", "/*", "#", "--"],
         "correct_option": 2, "explanation": "The '#' character begins a single-line comment in Python."},
        {"id": 8, "topic": "Syntax", "difficulty": "Medium",
         "question": "Which of the following is an invalid identifier in Python?",
         "options": ["_my_var", "var_2", "2nd_var", "myVar"],
         "correct_option": 2, "explanation": "Identifiers cannot start with a digit in Python."},
        {"id": 9, "topic": "Syntax", "difficulty": "Medium",
         "question": "What is the result of writing multiple statements on one line separated by semicolons in Python?",
         "options": ["SyntaxError", "Valid syntax", "Warning from linter only", "RuntimeError"],
         "correct_option": 1, "explanation": "Python syntax allows multiple statements separated by semicolons on a single line, though discouraged by PEP 8."},

        # Data Types & Variables (5)
        {"id": 10, "topic": "Data Types", "difficulty": "Easy",
         "question": "Which of the following data types is mutable in Python?",
         "options": ["tuple", "int", "list", "str"],
         "correct_option": 2, "explanation": "Lists in Python are mutable, meaning their contents can be altered in place."},
        {"id": 11, "topic": "Data Types", "difficulty": "Easy",
         "question": "What is the return type of `type(5 / 2)` in Python 3?",
         "options": ["int", "float", "double", "decimal"],
         "correct_option": 1, "explanation": "True division '/' always yields a float in Python 3."},
        {"id": 12, "topic": "Data Types", "difficulty": "Medium",
         "question": "What will `bool([])` and `bool([0])` evaluate to?",
         "options": ["True, True", "False, True", "False, False", "True, False"],
         "correct_option": 1, "explanation": "An empty list evaluates to False, whereas a non-empty list (even containing 0) evaluates to True."},
        {"id": 13, "topic": "Data Types", "difficulty": "Medium",
         "question": "What is the result of `type({})` in Python?",
         "options": ["set", "dict", "tuple", "NoneType"],
         "correct_option": 1, "explanation": "Empty curly braces `{}` create an empty dictionary; `set()` creates an empty set."},
        {"id": 14, "topic": "Data Types", "difficulty": "Hard",
         "question": "What is the maximum value an integer can hold in Python 3?",
         "options": ["2^31 - 1", "2^63 - 1", "2^127 - 1", "Virtually unlimited, bounded only by available RAM"],
         "correct_option": 3, "explanation": "Python 3 supports arbitrarily large integers with arbitrary precision, constrained only by system memory."},

        # Operators (4)
        {"id": 15, "topic": "Operators", "difficulty": "Easy",
         "question": "What is the output of `2 ** 3` in Python?",
         "options": ["6", "8", "9", "5"],
         "correct_option": 1, "explanation": "`**` is the exponentiation operator in Python; 2 ** 3 = 8."},
        {"id": 16, "topic": "Operators", "difficulty": "Easy",
         "question": "What does the `//` operator perform in Python?",
         "options": ["Comment", "Floating division", "Floor / Integer division", "Modulo"],
         "correct_option": 2, "explanation": "`//` computes integer floor division, discarding the fractional part."},
        {"id": 17, "topic": "Operators", "difficulty": "Medium",
         "question": "What is the difference between `==` and `is` in Python?",
         "options": ["`==` checks identity, `is` checks value", "`==` checks value equality, `is` checks object memory identity", "There is no difference", "`is` operates only on strings"],
         "correct_option": 1, "explanation": "`==` compares values (equality), whereas `is` checks whether both operands refer to the exact same object in memory."},
        {"id": 18, "topic": "Operators", "difficulty": "Hard",
         "question": "What is the result of `not 0 and 1 or 2`?",
         "options": ["False", "0", "1", "2"],
         "correct_option": 2, "explanation": "`not 0` is True. `True and 1` evaluates to 1. `1 or 2` short-circuits to 1."},

        # Control Statements & Loops (5)
        {"id": 19, "topic": "Control Statements", "difficulty": "Easy",
         "question": "Which keyword is used for 'else if' in Python conditional branches?",
         "options": ["else if", "elseif", "elif", "case"],
         "correct_option": 2, "explanation": "Python uses `elif` for chained conditions."},
        {"id": 20, "topic": "Control Statements", "difficulty": "Easy",
         "question": "Which statement terminates a loop immediately in Python?",
         "options": ["stop", "exit", "break", "continue"],
         "correct_option": 2, "explanation": "`break` terminates the nearest enclosing loop."},
        {"id": 21, "topic": "Control Statements", "difficulty": "Medium",
         "question": "What happens when an `else` block is attached to a `for` loop in Python?",
         "options": ["It never executes", "It executes if the loop terminates normally without encountering a `break`", "It executes only if an error occurs", "It executes on every iteration"],
         "correct_option": 1, "explanation": "A for/while loop's `else` clause executes when the loop finishes naturally without breaking."},
        {"id": 22, "topic": "Control Statements", "difficulty": "Medium",
         "question": "What is the output of `list(range(1, 6, 2))`?",
         "options": ["[1, 2, 3, 4, 5]", "[1, 3, 5]", "[2, 4, 6]", "[1, 3]"],
         "correct_option": 1, "explanation": "range(start, stop, step) with start=1, stop=6, step=2 produces 1, 3, 5."},
        {"id": 23, "topic": "Control Statements", "difficulty": "Hard",
         "question": "What statement serves as a null syntactic placeholder in Python?",
         "options": ["null", "nil", "void", "pass"],
         "correct_option": 3, "explanation": "`pass` is a null statement used when a statement is required syntactically but no code should execute."},

        # Functions & Scopes (5)
        {"id": 24, "topic": "Functions", "difficulty": "Easy",
         "question": "What keyword creates an anonymous inline function in Python?",
         "options": ["inline", "anon", "lambda", "def"],
         "correct_option": 2, "explanation": "`lambda` creates small anonymous functions."},
        {"id": 25, "topic": "Functions", "difficulty": "Easy",
         "question": "What is the default return value of a Python function that does not contain a return statement?",
         "options": ["0", "False", "None", "undefined"],
         "correct_option": 2, "explanation": "Functions without an explicit return statement return `None`."},
        {"id": 26, "topic": "Functions", "difficulty": "Medium",
         "question": "What does `*args` and `**kwargs` allow in a function definition?",
         "options": ["Only integer and string arguments", "Variable number of positional and keyword arguments", "Pointer arithmetic", "Multi-threading parameters"],
         "correct_option": 1, "explanation": "`*args` captures arbitrary positional arguments as a tuple, while `**kwargs` captures arbitrary keyword arguments as a dict."},
        {"id": 27, "topic": "Functions", "difficulty": "Medium",
         "question": "What is a major danger of using a mutable default argument (like `def foo(a=[]):`) in Python?",
         "options": ["It throws a SyntaxError", "The default object is created once at definition and shared across subsequent calls", "It causes memory allocation failure", "It slows down CPU execution"],
         "correct_option": 1, "explanation": "Default parameter values are evaluated once when the function definition is executed, making mutable defaults persist across calls."},
        {"id": 28, "topic": "Functions", "difficulty": "Hard",
         "question": "Which scope resolution rule does Python follow?",
         "options": ["BELF", "LEGB (Local, Enclosing, Global, Built-in)", "GELB", "FIFO"],
         "correct_option": 1, "explanation": "Python resolves variables according to the LEGB rule: Local, Enclosing, Global, and Built-in."},

        # Arrays & Collections (5)
        {"id": 29, "topic": "Arrays & Collections", "difficulty": "Easy",
         "question": "Which method adds an element to the end of a list in Python?",
         "options": ["add()", "insert()", "append()", "push()"],
         "correct_option": 2, "explanation": "`append()` appends a single item to the end of a list."},
        {"id": 30, "topic": "Arrays & Collections", "difficulty": "Easy",
         "question": "How do you access the last item of a list `lst` in Python?",
         "options": ["lst[len(lst)]", "lst[-1]", "lst.last()", "lst.pop()"],
         "correct_option": 1, "explanation": "Negative indexing in Python allows `lst[-1]` to refer to the last item."},
        {"id": 31, "topic": "Arrays & Collections", "difficulty": "Medium",
         "question": "What is the output of `[x*2 for x in range(3)]`?",
         "options": ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "[0, 2]"],
         "correct_option": 0, "explanation": "List comprehension multiplying 0, 1, 2 by 2 yields [0, 2, 4]."},
        {"id": 32, "topic": "Arrays & Collections", "difficulty": "Medium",
         "question": "Which data structure guarantees uniqueness of its elements?",
         "options": ["list", "tuple", "set", "dict"],
         "correct_option": 2, "explanation": "Sets in Python store unordered unique elements."},
        {"id": 33, "topic": "Arrays & Collections", "difficulty": "Hard",
         "question": "What is the average time complexity of key lookup in a Python dictionary?",
         "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
         "correct_option": 2, "explanation": "Python dictionaries are implemented with hash tables, providing O(1) average time complexity for lookups."},

        # OOP Concepts (5)
        {"id": 34, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "What is the first parameter of an instance method in a Python class typically named?",
         "options": ["this", "self", "cls", "instance"],
         "correct_option": 1, "explanation": "By convention, instance methods take `self` as their first parameter representing the instance."},
        {"id": 35, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "Which method is called when an object is instantiated?",
         "options": ["__new__", "__init__", "__start__", "__main__"],
         "correct_option": 1, "explanation": "`__init__` acts as the class initializer/constructor."},
        {"id": 36, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "How does Python achieve inheritance between a subclass `Child` and superclass `Parent`?",
         "options": ["class Child extends Parent:", "class Child implements Parent:", "class Child(Parent):", "class Child: inherit Parent"],
         "correct_option": 2, "explanation": "Python uses parenthesis syntax `class Child(Parent):` to specify inheritance."},
        {"id": 37, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "What does `@staticmethod` indicate in Python?",
         "options": ["Method cannot modify class state and takes neither `self` nor `cls`", "Method that cannot be overridden", "Method that returns a constant", "Private instance method"],
         "correct_option": 0, "explanation": "A `@staticmethod` does not receive an implicit first argument (`self` or `cls`)."},
        {"id": 38, "topic": "OOP Concepts", "difficulty": "Hard",
         "question": "What is the Method Resolution Order (MRO) algorithm used in Python 3?",
         "options": ["Depth-First Search", "Breadth-First Search", "C3 Linearization", "Dijkstra Algorithm"],
         "correct_option": 2, "explanation": "Python 3 uses the C3 Linearization algorithm to determine the MRO for multiple inheritance."},

        # Exception Handling (4)
        {"id": 39, "topic": "Exception Handling", "difficulty": "Easy",
         "question": "Which block is used to catch exceptions in Python?",
         "options": ["try ... catch", "try ... except", "catch ... finally", "attempt ... trap"],
         "correct_option": 1, "explanation": "Python uses `try` and `except` blocks for handling exceptions."},
        {"id": 40, "topic": "Exception Handling", "difficulty": "Easy",
         "question": "Which keyword is used to trigger an exception intentionally?",
         "options": ["throw", "raise", "error", "catch"],
         "correct_option": 1, "explanation": "`raise` is used to raise an exception in Python."},
        {"id": 41, "topic": "Exception Handling", "difficulty": "Medium",
         "question": "When does the `finally` block execute in Python?",
         "options": ["Only if an exception is raised", "Only if no exception is raised", "Always, whether an exception occurred or not", "Only if caught by `except`"],
         "correct_option": 2, "explanation": "The `finally` block always executes under all circumstances, typically for cleanup."},
        {"id": 42, "topic": "Exception Handling", "difficulty": "Hard",
         "question": "What base class should custom user-defined exceptions inherit from in Python?",
         "options": ["BaseException", "Exception", "Error", "StandardError"],
         "correct_option": 1, "explanation": "Custom exceptions should inherit from `Exception`, not `BaseException` (which is reserved for system-exiting exceptions like KeyboardInterrupt)."},

        # Problem Solving & Advanced (8)
        {"id": 43, "topic": "Problem Solving", "difficulty": "Easy",
         "question": "What will `len('Python')` return?",
         "options": ["5", "6", "7", "0"],
         "correct_option": 1, "explanation": "'Python' has 6 characters."},
        {"id": 44, "topic": "Problem Solving", "difficulty": "Medium",
         "question": "How can you reverse a list `a` using slicing in Python?",
         "options": ["a[0:-1]", "a[::-1]", "a[::0]", "a[1::-1]"],
         "correct_option": 1, "explanation": "`a[::-1]` produces a reversed shallow copy of the sequence."},
        {"id": 45, "topic": "Advanced Concepts", "difficulty": "Medium",
         "question": "What keyword turns a normal function into a generator in Python?",
         "options": ["generate", "return", "yield", "next"],
         "correct_option": 2, "explanation": "The `yield` keyword pauses function execution and produces an iterator generator object."},
        {"id": 46, "topic": "Advanced Concepts", "difficulty": "Medium",
         "question": "What is a decorator in Python?",
         "options": ["A graphical interface tool", "A function that takes another function and extends its behavior without modifying it", "A class destructor", "A memory profiler"],
         "correct_option": 1, "explanation": "A decorator is a callable that takes a function as argument and returns a modified or wrapped function."},
        {"id": 47, "topic": "Advanced Concepts", "difficulty": "Hard",
         "question": "What is the purpose of the `__slots__` attribute in a Python class?",
         "options": ["Enables multithreading support", "Prevents the creation of `__dict__`, conserving memory and speeding attribute access", "Creates slot machine GUI elements", "Defines database table foreign keys"],
         "correct_option": 1, "explanation": "`__slots__` explicitly declares instance attributes and inhibits `__dict__`, reducing per-instance memory footprint."},
        {"id": 48, "topic": "Advanced Concepts", "difficulty": "Hard",
         "question": "What does `functools.lru_cache` do?",
         "options": ["Caches database connections", "Memoizes function return values up to a maxsize using Least Recently Used replacement", "Flushes CPU L1 cache", "Compresses string objects"],
         "correct_option": 1, "explanation": "`lru_cache` wraps a function with a memoizing callable that saves recent calls and results up to maxsize."},
        {"id": 49, "topic": "Advanced Concepts", "difficulty": "Hard",
         "question": "Which module in Python is used for serialization and deserialization of objects into byte streams?",
         "options": ["json", "serialize", "pickle", "marshal"],
         "correct_option": 2, "explanation": "The `pickle` module serializes arbitrary Python object hierarchies into byte streams."},
        {"id": 50, "topic": "Advanced Concepts", "difficulty": "Hard",
         "question": "What is the purpose of the `contextlib` module and `__enter__` / `__exit__` dunder methods?",
         "options": ["Implementing Context Managers with the `with` statement", "Configuring web application server contexts", "Managing database thread locks only", "Garbage collection hooks"],
         "correct_option": 0, "explanation": "`__enter__` and `__exit__` define the context manager protocol, invoked by Python's `with` statement."}
    ]

    coding = [
        {
            "id": 51,
            "title": "Subarray Target Sum Locator",
            "skill": "Python",
            "domain": "Algorithms & Problem Solving",
            "topic": "Arrays & Two Pointers",
            "difficulty": "Intermediate",
            "problem_statement": "Given an integer array `nums` and an integer `target`, return the 0-based start and end indices `[start, end]` of a contiguous non-empty subarray that sums to `target`.\nIf multiple subarrays exist, return the first one found.\nIf no such subarray exists, return `[-1, -1]`.",
            "input_format": "List of integers `nums` and integer `target`.",
            "output_format": "List of two integers `[start_index, end_index]` or `[-1, -1]`.",
            "constraints": "1 <= len(nums) <= 10000, 1 <= target <= 10^9, 1 <= nums[i] <= 10^5",
            "function_name": "find_target_subarray",
            "code_template": "def find_target_subarray(nums: list, target: int) -> list:\n    # Write your solution here\n    # Return [start_index, end_index] or [-1, -1]\n    pass\n",
            "test_cases": [
                {"input": {"nums": [1, 2, 3, 7, 5], "target": 12}, "expected": [1, 3], "is_hidden": False},
                {"input": {"nums": [1, 4, 0, 0, 3, 10, 5], "target": 7}, "expected": [1, 4], "is_hidden": False},
                {"input": {"nums": [1, 2, 3, 4, 5], "target": 100}, "expected": [-1, -1], "is_hidden": True},
                {"input": {"nums": [5], "target": 5}, "expected": [0, 0], "is_hidden": True},
                {"input": {"nums": [2, 4, 6, 8, 10], "target": 14}, "expected": [2, 3], "is_hidden": True}
            ]
        },
        {
            "id": 52,
            "title": "Valid Bracket Sequence Validator",
            "skill": "Python",
            "domain": "Data Structures & Parsing",
            "topic": "Stacks & Strings",
            "difficulty": "Intermediate",
            "problem_statement": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
            "input_format": "String `s` containing brackets.",
            "output_format": "Boolean `True` or `False`.",
            "constraints": "0 <= len(s) <= 10000. String consists of parentheses only '()[]{}'.",
            "function_name": "is_valid_brackets",
            "code_template": "def is_valid_brackets(s: str) -> bool:\n    # Write your solution here\n    # Return True if valid, False otherwise\n    pass\n",
            "test_cases": [
                {"input": {"s": "()[]{}"}, "expected": True, "is_hidden": False},
                {"input": {"s": "(]"}, "expected": False, "is_hidden": False},
                {"input": {"s": "([{}])"}, "expected": True, "is_hidden": True},
                {"input": {"s": "((("}, "expected": False, "is_hidden": True},
                {"input": {"s": ""}, "expected": True, "is_hidden": True},
                {"input": {"s": "{[]()}"}, "expected": True, "is_hidden": True}
            ]
        }
    ]
    return {"mcqs": mcqs, "coding": coding}


def create_sql_bank():
    mcqs = [
        # Database Concepts & Architecture (5)
        {"id": 1, "topic": "Database Concepts", "difficulty": "Easy",
         "question": "What does SQL stand for?",
         "options": ["Structured Query Language", "Sequential Query Logic", "System Question Language", "Standard Quality Language"],
         "correct_option": 0, "explanation": "SQL stands for Structured Query Language."},
        {"id": 2, "topic": "Database Concepts", "difficulty": "Easy",
         "question": "Which of the following is a Relational Database Management System (RDBMS)?",
         "options": ["MongoDB", "PostgreSQL", "Redis", "Cassandra"],
         "correct_option": 1, "explanation": "PostgreSQL is an enterprise-grade open source relational database."},
        {"id": 3, "topic": "Database Concepts", "difficulty": "Medium",
         "question": "What is the relational model term for a row in a table?",
         "options": ["Attribute", "Tuple", "Domain", "Relation"],
         "correct_option": 1, "explanation": "In relational database theory, a row is formally called a tuple."},
        {"id": 4, "topic": "Database Concepts", "difficulty": "Medium",
         "question": "What is the primary objective of Database Normalization?",
         "options": ["Maximize data redundancy", "Minimize data redundancy and prevent anomalies", "Increase table size", "Eliminate all foreign keys"],
         "correct_option": 1, "explanation": "Normalization organizes fields and tables to minimize redundancy and prevent insertion, update, and deletion anomalies."},
        {"id": 5, "topic": "Database Concepts", "difficulty": "Hard",
         "question": "A table is in Third Normal Form (3NF) if it is in 2NF and has no what?",
         "options": ["Composite primary keys", "Transitive functional dependencies", "Foreign keys", "Null values"],
         "correct_option": 1, "explanation": "3NF requires that all non-key attributes are directly dependent on the primary key, eliminating transitive dependencies."},

        # DDL & Schema Definition (5)
        {"id": 6, "topic": "DDL & Schema", "difficulty": "Easy",
         "question": "Which SQL statement is used to create a new database table?",
         "options": ["NEW TABLE", "CREATE TABLE", "MAKE TABLE", "INSERT TABLE"],
         "correct_option": 1, "explanation": "`CREATE TABLE` is the standard DDL command to define new tables."},
        {"id": 7, "topic": "DDL & Schema", "difficulty": "Easy",
         "question": "Which command removes a table and all its structural definitions permanently?",
         "options": ["DELETE TABLE", "REMOVE TABLE", "DROP TABLE", "CLEAR TABLE"],
         "correct_option": 2, "explanation": "`DROP TABLE` permanently deletes the table structure and its rows from the database."},
        {"id": 8, "topic": "DDL & Schema", "difficulty": "Medium",
         "question": "What is the difference between `TRUNCATE` and `DELETE` without a WHERE clause?",
         "options": ["DELETE is DDL while TRUNCATE is DML", "TRUNCATE deallocates data pages quickly and cannot be selectively filtered; DELETE removes rows individually", "There is no difference", "DELETE drops the table structure"],
         "correct_option": 1, "explanation": "`TRUNCATE` is a DDL operation that swiftly deallocates table extents, whereas `DELETE` is a row-by-row DML operation."},
        {"id": 9, "topic": "DDL & Schema", "difficulty": "Medium",
         "question": "Which SQL clause modifies the structure of an existing table by adding a column?",
         "options": ["UPDATE TABLE ADD", "ALTER TABLE ADD COLUMN", "MODIFY TABLE WITH", "CHANGE TABLE"],
         "correct_option": 1, "explanation": "`ALTER TABLE table_name ADD COLUMN column_name datatype;` adds a new column."},
        {"id": 10, "topic": "DDL & Schema", "difficulty": "Hard",
         "question": "What does the `CASCADE` option do when dropping a primary key or table?",
         "options": ["Backs up data to disk", "Automatically drops any dependent foreign key constraints or objects referencing it", "Prevents dropping if references exist", "Compresses table indexes"],
         "correct_option": 1, "explanation": "`CASCADE` automatically removes any dependent objects or foreign key constraints referencing the target."},

        # DML & Basic Queries (5)
        {"id": 11, "topic": "Basic Queries", "difficulty": "Easy",
         "question": "Which SQL keyword is used to retrieve data from a database?",
         "options": ["GET", "FETCH", "SELECT", "PULL"],
         "correct_option": 2, "explanation": "`SELECT` is the core SQL statement used to query and retrieve data."},
        {"id": 12, "topic": "Basic Queries", "difficulty": "Easy",
         "question": "Which clause is used to eliminate duplicate rows from the query output?",
         "options": ["UNIQUE", "DISTINCT", "DIFFERENT", "FILTER"],
         "correct_option": 1, "explanation": "`SELECT DISTINCT` filters out duplicate rows from the result set."},
        {"id": 13, "topic": "Basic Queries", "difficulty": "Medium",
         "question": "Which clause is used to sort the result set in descending order?",
         "options": ["ORDER BY col DESC", "SORT BY col DOWN", "GROUP BY col DESC", "ALIGN col DESC"],
         "correct_option": 0, "explanation": "`ORDER BY column DESC` sorts results in descending order."},
        {"id": 14, "topic": "Basic Queries", "difficulty": "Medium",
         "question": "Which SQL clause restricts the total number of rows returned in MySQL/PostgreSQL/SQLite?",
         "options": ["TOP", "ROWCOUNT", "LIMIT", "MAXROWS"],
         "correct_option": 2, "explanation": "`LIMIT n` caps the number of records returned."},
        {"id": 15, "topic": "Basic Queries", "difficulty": "Hard",
         "question": "In what logical order does a relational database evaluate a SELECT query?",
         "options": ["SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY", "FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY", "WHERE, FROM, GROUP BY, SELECT, ORDER BY", "FROM, SELECT, WHERE, ORDER BY"],
         "correct_option": 1, "explanation": "Logically, queries are executed in order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT."},

        # Operators & Conditions (5)
        {"id": 16, "topic": "Operators & Conditions", "difficulty": "Easy",
         "question": "Which operator filters for values matching a specified pattern in text?",
         "options": ["MATCH", "LIKE", "CONTAINS", "SIMILAR"],
         "correct_option": 1, "explanation": "`LIKE` is used in WHERE clauses for pattern matching using wildcard characters."},
        {"id": 17, "topic": "Operators & Conditions", "difficulty": "Easy",
         "question": "In a `LIKE` pattern, which character represents zero, one, or multiple characters?",
         "options": ["?", "_", "%", "*"],
         "correct_option": 2, "explanation": "`%` represents any string of zero or more characters in SQL LIKE patterns."},
        {"id": 18, "topic": "Operators & Conditions", "difficulty": "Medium",
         "question": "How do you test if a column contains a NULL value in SQL?",
         "options": ["col == NULL", "col = NULL", "col IS NULL", "col.isNull()"],
         "correct_option": 2, "explanation": "In three-valued logic, equality comparison with NULL yields unknown; `IS NULL` is required."},
        {"id": 19, "topic": "Operators & Conditions", "difficulty": "Medium",
         "question": "Which operator checks if a value exists within an inclusive range?",
         "options": ["WITHIN", "BETWEEN", "RANGE", "INSIDE"],
         "correct_option": 1, "explanation": "`BETWEEN low AND high` checks for inclusive range membership."},
        {"id": 20, "topic": "Operators & Conditions", "difficulty": "Hard",
         "question": "What is the truth value of `NULL = NULL` in standard SQL?",
         "options": ["TRUE", "FALSE", "UNKNOWN (NULL)", "Error"],
         "correct_option": 2, "explanation": "Standard SQL uses three-valued logic (True, False, Unknown); comparing NULL to NULL evaluates to Unknown."},

        # Aggregation & GROUP BY (5)
        {"id": 21, "topic": "Aggregation", "difficulty": "Easy",
         "question": "Which function calculates the total sum of a numeric column in SQL?",
         "options": ["TOTAL()", "SUM()", "COUNT()", "ADD()"],
         "correct_option": 1, "explanation": "`SUM()` returns the arithmetic sum of values."},
        {"id": 22, "topic": "Aggregation", "difficulty": "Easy",
         "question": "What is the difference between `COUNT(*)` and `COUNT(column_name)`?",
         "options": ["COUNT(*) counts all rows including NULLs; COUNT(column_name) ignores NULLs", "COUNT(*) ignores NULLs", "There is no difference", "COUNT(column_name) returns distinct values"],
         "correct_option": 0, "explanation": "`COUNT(*)` counts all rows regardless of NULLs; `COUNT(col)` excludes NULL values."},
        {"id": 23, "topic": "Aggregation", "difficulty": "Medium",
         "question": "Which clause is used to filter groups created by `GROUP BY`?",
         "options": ["WHERE", "FILTER", "HAVING", "QUALIFY"],
         "correct_option": 2, "explanation": "`HAVING` filters grouped rows after aggregation, whereas `WHERE` filters individual rows prior to grouping."},
        {"id": 24, "topic": "Aggregation", "difficulty": "Medium",
         "question": "What happens if a column in the SELECT list is neither aggregated nor included in the `GROUP BY` clause?",
         "options": ["It is assigned a random value", "Most SQL standards reject it with a syntax error", "It is automatically averaged", "It returns NULL"],
         "correct_option": 1, "explanation": "In standard SQL, non-aggregated columns in SELECT must appear in the GROUP BY clause."},
        {"id": 25, "topic": "Aggregation", "difficulty": "Hard",
         "question": "Which aggregate function ignores NULLs and computes the population standard deviation in SQL?",
         "options": ["STDDEV_POP()", "VAR_POP()", "AVG_DEV()", "DEV()"],
         "correct_option": 0, "explanation": "`STDDEV_POP()` computes population standard deviation."},

        # Joins & Relational Algebra (5)
        {"id": 26, "topic": "Joins", "difficulty": "Easy",
         "question": "Which JOIN returns records that have matching values in both tables?",
         "options": ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"],
         "correct_option": 2, "explanation": "`INNER JOIN` selects records where there is a match in both left and right tables."},
        {"id": 27, "topic": "Joins", "difficulty": "Easy",
         "question": "Which JOIN returns all records from the left table, and the matched records from the right table?",
         "options": ["LEFT (OUTER) JOIN", "RIGHT JOIN", "CROSS JOIN", "INNER JOIN"],
         "correct_option": 0, "explanation": "`LEFT JOIN` returns all rows from the left table with matching values or NULLs for the right table."},
        {"id": 28, "topic": "Joins", "difficulty": "Medium",
         "question": "What is the Cartesian product of two tables producing all possible row combinations called?",
         "options": ["NATURAL JOIN", "CROSS JOIN", "SELF JOIN", "INNER JOIN"],
         "correct_option": 1, "explanation": "`CROSS JOIN` produces the Cartesian product of rows from both tables."},
        {"id": 29, "topic": "Joins", "difficulty": "Medium",
         "question": "What type of join joins a table to itself?",
         "options": ["SELF JOIN", "AUTO JOIN", "CIRCULAR JOIN", "LOOP JOIN"],
         "correct_option": 0, "explanation": "A `SELF JOIN` joins a table with itself, typically aliasing the table twice."},
        {"id": 30, "topic": "Joins", "difficulty": "Hard",
         "question": "If Table A has 5 rows and Table B has 4 rows, how many rows will `A CROSS JOIN B` yield?",
         "options": ["9", "20", "5", "1"],
         "correct_option": 1, "explanation": "A Cartesian product generates 5 * 4 = 20 rows."},

        # Subqueries & CTEs (5)
        {"id": 31, "topic": "Subqueries & CTEs", "difficulty": "Easy",
         "question": "What is a query nested inside another SQL statement called?",
         "options": ["Join", "Subquery / Inner query", "Trigger", "View"],
         "correct_option": 1, "explanation": "A query nested inside a SELECT, INSERT, UPDATE, or DELETE is a subquery."},
        {"id": 32, "topic": "Subqueries & CTEs", "difficulty": "Medium",
         "question": "What keyword defines a Common Table Expression (CTE) in SQL?",
         "options": ["CREATE CTE", "WITH", "DECLARE", "TEMP"],
         "correct_option": 1, "explanation": "`WITH cte_name AS (...)` defines a Common Table Expression."},
        {"id": 33, "topic": "Subqueries & CTEs", "difficulty": "Medium",
         "question": "What characterizes a correlated subquery?",
         "options": ["It references columns from the outer query and evaluates once per outer row", "It executes only once independently of the outer query", "It must return a single string", "It cannot use WHERE clauses"],
         "correct_option": 0, "explanation": "A correlated subquery references columns from the outer query, evaluating once for each row evaluated by the outer query."},
        {"id": 34, "topic": "Subqueries & CTEs", "difficulty": "Hard",
         "question": "Which operator returns TRUE if a subquery returns at least one row?",
         "options": ["ANY", "EXISTS", "CONTAINS", "IN"],
         "correct_option": 1, "explanation": "`EXISTS (SELECT ...)` evaluates to TRUE if the subquery returns one or more rows."},
        {"id": 35, "topic": "Subqueries & CTEs", "difficulty": "Hard",
         "question": "What is a recursive CTE commonly used for?",
         "options": ["Querying hierarchical or tree-structured data like org charts and graph paths", "Fast password encryption", "Replacing index scans with full table scans", "Auto-generating primary keys"],
         "correct_option": 0, "explanation": "Recursive CTEs iteratively query hierarchical, tree, or graph relationships."},

        # Constraints, Keys & Indexes (5)
        {"id": 36, "topic": "Constraints & Indexes", "difficulty": "Easy",
         "question": "Which constraint uniquely identifies each record in a database table?",
         "options": ["FOREIGN KEY", "UNIQUE", "PRIMARY KEY", "CHECK"],
         "correct_option": 2, "explanation": "A PRIMARY KEY uniquely identifies each record and cannot contain NULLs."},
        {"id": 37, "topic": "Constraints & Indexes", "difficulty": "Easy",
         "question": "What does a FOREIGN KEY constraint maintain between two tables?",
         "options": ["Execution speed", "Referential integrity", "Storage compression", "Data encryption"],
         "correct_option": 1, "explanation": "Foreign keys enforce referential integrity between child and parent tables."},
        {"id": 38, "topic": "Constraints & Indexes", "difficulty": "Medium",
         "question": "What constraint limits the values that can be entered into a column by evaluating a logical condition?",
         "options": ["DEFAULT", "CHECK", "INDEX", "NOT NULL"],
         "correct_option": 1, "explanation": "`CHECK (condition)` ensures column values satisfy a specified Boolean predicate."},
        {"id": 39, "topic": "Constraints & Indexes", "difficulty": "Medium",
         "question": "What is the primary benefit of adding a B-Tree index to a database column?",
         "options": ["Accelerates SELECT search queries", "Accelerates INSERT operations", "Reduces disk space", "Encrypts column data"],
         "correct_option": 0, "explanation": "B-Tree indexes speed up lookups and range queries by reducing the rows scanned."},
        {"id": 40, "topic": "Constraints & Indexes", "difficulty": "Hard",
         "question": "What is the trade-off of maintaining multiple indexes on a table?",
         "options": ["Slows down SELECT queries", "Degrades INSERT, UPDATE, and DELETE performance due to index maintenance overhead", "Disables transactions", "Restricts table to 1000 rows"],
         "correct_option": 1, "explanation": "Every index must be updated on DML writes (INSERT/UPDATE/DELETE), adding performance overhead."},

        # Transactions & ACID Properties (5)
        {"id": 41, "topic": "Transactions & ACID", "difficulty": "Easy",
         "question": "What does the 'A' in ACID properties stand for?",
         "options": ["Availability", "Atomicity", "Accuracy", "Allocation"],
         "correct_option": 1, "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability."},
        {"id": 42, "topic": "Transactions & ACID", "difficulty": "Medium",
         "question": "Which SQL command saves all changes made during the current transaction permanently?",
         "options": ["SAVE", "COMMIT", "ROLLBACK", "APPLY"],
         "correct_option": 1, "explanation": "`COMMIT` finalizes and saves all modifications of the current transaction."},
        {"id": 43, "topic": "Transactions & ACID", "difficulty": "Medium",
         "question": "Which command rolls back transaction changes to the beginning or to a designated point?",
         "options": ["RESET", "ROLLBACK", "REVERT", "UNDO"],
         "correct_option": 1, "explanation": "`RESET` resets transaction state; `ROLLBACK` undoes uncommitted transaction changes."},
        {"id": 44, "topic": "Transactions & ACID", "difficulty": "Hard",
         "question": "Which isolation level prevents Dirty Reads, Non-repeatable Reads, and Phantom Reads completely?",
         "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"],
         "correct_option": 3, "explanation": "`Serializable` is the strictest ANSI isolation level, preventing all concurrency anomalies."},
        {"id": 45, "topic": "Transactions & ACID", "difficulty": "Hard",
         "question": "What phenomenon occurs when a transaction reads uncommitted changes from another concurrent transaction?",
         "options": ["Phantom Read", "Dirty Read", "Non-repeatable Read", "Lost Update"],
         "correct_option": 1, "explanation": "A Dirty Read occurs when a transaction reads dirty/uncommitted data modified by another concurrent transaction."},

        # Advanced SQL & Window Functions (5)
        {"id": 46, "topic": "Advanced SQL", "difficulty": "Medium",
         "question": "Which SQL clause partitions rows into subsets for window function calculations?",
         "options": ["GROUP BY", "PARTITION BY", "SPLIT BY", "DIVIDE BY"],
         "correct_option": 1, "explanation": "`OVER (PARTITION BY ...)` defines row subsets for window functions."},
        {"id": 47, "topic": "Advanced SQL", "difficulty": "Medium",
         "question": "What is the difference between `RANK()` and `DENSE_RANK()`?",
         "options": ["RANK leaves gaps in rankings after ties; DENSE_RANK assigns consecutive numbers without gaps", "DENSE_RANK only works on numeric columns", "RANK skips all duplicates", "There is no difference"],
         "correct_option": 0, "explanation": "`RANK()` skips subsequent ranks upon ties (e.g. 1, 2, 2, 4), while `DENSE_RANK()` leaves no gaps (1, 2, 2, 3)."},
        {"id": 48, "topic": "Advanced SQL", "difficulty": "Hard",
         "question": "Which window function accesses data from a subsequent row without requiring a self-join?",
         "options": ["LAG()", "LEAD()", "NEXT()", "FORWARD()"],
         "correct_option": 1, "explanation": "`LEAD(col, offset)` accesses a value from a succeeding row."},
        {"id": 49, "topic": "Advanced SQL", "difficulty": "Hard",
         "question": "What does `COALESCE(val1, val2, val3)` return?",
         "options": ["The arithmetic mean of the values", "The first non-null expression in its argument list", "TRUE if any is NULL", "A concatenated string"],
         "correct_option": 1, "explanation": "`COALESCE` evaluates its arguments in order and returns the first non-null value."},
        {"id": 50, "topic": "Advanced SQL", "difficulty": "Hard",
         "question": "What does a VIEW in a database represent?",
         "options": ["A physical table stored on high-speed NVMe memory", "A saved SQL query representing a virtual table computed dynamically or materialized", "A database index", "A user permission token"],
         "correct_option": 1, "explanation": "A VIEW is a virtual table defined by a stored SELECT query."}
    ]

    coding = [
        {
            "id": 51,
            "title": "Department High Earner Report",
            "skill": "SQL",
            "domain": "Relational Querying & Aggregation",
            "topic": "JOIN & GROUP BY",
            "difficulty": "Intermediate",
            "problem_statement": "You are given two tables in an SQLite database: `departments` and `employees`.\n\n`departments` schema:\n- `id` (INTEGER PRIMARY KEY)\n- `name` (TEXT)\n\n`employees` schema:\n- `id` (INTEGER PRIMARY KEY)\n- `name` (TEXT)\n- `salary` (INTEGER)\n- `department_id` (INTEGER, FOREIGN KEY to departments.id)\n\nWrite a SQL query that retrieves each department's name, total number of employees (`employee_count`), and highest salary (`max_salary`).\nOrder the results by `max_salary` descending, then by `department_name` ascending.",
            "input_format": "Query runs against SQLite in-memory database with populated `departments` and `employees` tables.",
            "output_format": "Columns: `department_name`, `employee_count`, `max_salary`.",
            "constraints": "Return only departments that have at least 1 employee.",
            "function_name": "execute_query",
            "code_template": "-- Write your SQL query here\nSELECT \n  d.name AS department_name,\n  COUNT(e.id) AS employee_count,\n  MAX(e.salary) AS max_salary\nFROM departments d\nJOIN employees e ON d.id = e.department_id\nGROUP BY d.id, d.name\nORDER BY max_salary DESC, department_name ASC;\n",
            "schema_seed": """
CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary INTEGER, department_id INTEGER);

INSERT INTO departments VALUES (1, 'Engineering'), (2, 'Marketing'), (3, 'Human Resources'), (4, 'Sales');
INSERT INTO employees VALUES (101, 'Alice', 120000, 1);
INSERT INTO employees VALUES (102, 'Bob', 95000, 1);
INSERT INTO employees VALUES (103, 'Charlie', 80000, 2);
INSERT INTO employees VALUES (104, 'Diana', 110000, 2);
INSERT INTO employees VALUES (105, 'Eve', 65000, 3);
INSERT INTO employees VALUES (106, 'Frank', 135000, 4);
INSERT INTO employees VALUES (107, 'Grace', 90000, 4);
""",
            "test_cases": [
                {
                    "input": {},
                    "expected": [
                        ["Sales", 2, 135000],
                        ["Engineering", 2, 120000],
                        ["Marketing", 2, 110000],
                        ["Human Resources", 1, 65000]
                    ],
                    "is_hidden": False
                },
                {
                    "input": {
                        "extra_seed": "INSERT INTO employees VALUES (108, 'Zack', 200000, 1);"
                    },
                    "expected": [
                        ["Engineering", 3, 200000],
                        ["Sales", 2, 135000],
                        ["Marketing", 2, 110000],
                        ["Human Resources", 1, 65000]
                    ],
                    "is_hidden": True
                }
            ]
        },
        {
            "id": 52,
            "title": "Customer Retention & Cumulative Spend Filter",
            "skill": "SQL",
            "domain": "Relational Filtering & Aggregations",
            "topic": "HAVING & Subqueries",
            "difficulty": "Intermediate",
            "problem_statement": "Given a `customers` table and an `orders` table in SQLite:\n\n`customers` schema:\n- `customer_id` (INTEGER PRIMARY KEY)\n- `customer_name` (TEXT)\n- `country` (TEXT)\n\n`orders` schema:\n- `order_id` (INTEGER PRIMARY KEY)\n- `customer_id` (INTEGER)\n- `order_amount` (REAL)\n\nWrite a SQL query to find all customers who have placed at least 2 orders AND have a cumulative order spend of at least 500.00.\nReturn `customer_name`, `country`, and the rounded cumulative spend as `total_spend`.\nOrder by `total_spend` descending.",
            "input_format": "Query runs against SQLite in-memory database with populated `customers` and `orders` tables.",
            "output_format": "Columns: `customer_name`, `country`, `total_spend`.",
            "constraints": "Only include customers meeting both order count >= 2 and total spend >= 500.00.",
            "function_name": "execute_query",
            "code_template": "-- Write your SQL query here\nSELECT \n  c.customer_name,\n  c.country,\n  ROUND(SUM(o.order_amount), 2) AS total_spend\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_id, c.customer_name, c.country\nHAVING COUNT(o.order_id) >= 2 AND SUM(o.order_amount) >= 500.00\nORDER BY total_spend DESC;\n",
            "schema_seed": """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, customer_name TEXT, country TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_amount REAL);

INSERT INTO customers VALUES (1, 'Acme Corp', 'USA'), (2, 'Globex Ltd', 'UK'), (3, 'Soylent Inc', 'Canada'), (4, 'Initech', 'USA');
INSERT INTO orders VALUES (101, 1, 250.50), (102, 1, 350.50); -- Acme: 2 orders, 601.00
INSERT INTO orders VALUES (103, 2, 700.00); -- Globex: 1 order (fails count >= 2)
INSERT INTO orders VALUES (104, 3, 200.00), (105, 3, 150.00), (106, 3, 50.00); -- Soylent: 3 orders, 400.00 (fails spend >= 500)
INSERT INTO orders VALUES (107, 4, 300.00), (108, 4, 450.00); -- Initech: 2 orders, 750.00
""",
            "test_cases": [
                {
                    "input": {},
                    "expected": [
                        ["Initech", "USA", 750.0],
                        ["Acme Corp", "USA", 601.0]
                    ],
                    "is_hidden": False
                },
                {
                    "input": {
                        "extra_seed": "INSERT INTO orders VALUES (109, 3, 200.00); -- Soylent now 600.00, count 4"
                    },
                    "expected": [
                        ["Initech", "USA", 750.0],
                        ["Acme Corp", "USA", 601.0],
                        ["Soylent Inc", "Canada", 600.0]
                    ],
                    "is_hidden": True
                }
            ]
        }
    ]
    return {"mcqs": mcqs, "coding": coding}


def create_java_bank():
    mcqs = [
        # Basic Concepts & JVM (5)
        {"id": 1, "topic": "Basic Concepts", "difficulty": "Easy",
         "question": "What makes Java a platform-independent language?",
         "options": ["Code is directly compiled to machine code for all CPUs", "Source code is compiled into bytecode executed by the Java Virtual Machine (JVM)", "It runs without a runtime engine", "It is an interpreted shell script"],
         "correct_option": 1, "explanation": "Java compiles source code into platform-independent bytecode (.class files) that any JVM can interpret or JIT-compile."},
        {"id": 2, "topic": "Basic Concepts", "difficulty": "Easy",
         "question": "What is the primary function of the JIT (Just-In-Time) compiler in the JVM?",
         "options": ["Checks source code syntax", "Compiles frequently executed bytecode into native machine code at runtime", "Manages source versioning", "Allocates heap space for classes"],
         "correct_option": 1, "explanation": "The JIT compiler compiles hotspots of bytecode directly into native machine code for faster execution."},
        {"id": 3, "topic": "Basic Concepts", "difficulty": "Medium",
         "question": "Which memory region in the JVM stores object instances?",
         "options": ["Stack", "Heap", "Method Area / Metaspace", "Program Counter (PC) Register"],
         "correct_option": 1, "explanation": "In Java, all objects are allocated on the Heap memory."},
        {"id": 4, "topic": "Basic Concepts", "difficulty": "Medium",
         "question": "What happens when an object on the heap no longer has any active references in Java?",
         "options": ["Throws NullPointerException", "Becomes eligible for automated Garbage Collection", "Causes memory lock", "Moves to the Stack"],
         "correct_option": 1, "explanation": "Unreferenced objects become eligible for automated reclamation by the Java Garbage Collector."},
        {"id": 5, "topic": "Basic Concepts", "difficulty": "Hard",
         "question": "What is the exact signature of the entry-point `main` method in a standard Java application?",
         "options": ["public void main(String args[])", "public static void main(String[] args)", "static void main(String[] args)", "public int main(String[] args)"],
         "correct_option": 1, "explanation": "Standard Java entry method must be `public static void main(String[] args)`."},

        # Syntax & Data Types (5)
        {"id": 6, "topic": "Syntax & Data Types", "difficulty": "Easy",
         "question": "Which of the following is NOT a primitive data type in Java?",
         "options": ["int", "boolean", "String", "double"],
         "correct_option": 2, "explanation": "`String` in Java is a reference class object, not a primitive data type."},
        {"id": 7, "topic": "Syntax & Data Types", "difficulty": "Easy",
         "question": "What is the size of the primitive `int` data type in Java?",
         "options": ["16 bits (2 bytes)", "32 bits (4 bytes)", "64 bits (8 bytes)", "Platform dependent"],
         "correct_option": 1, "explanation": "Java guarantees that `int` is always 32 bits (4 bytes) signed across all platforms."},
        {"id": 8, "topic": "Syntax & Data Types", "difficulty": "Medium",
         "question": "What is the default value of an uninitialized instance boolean field in Java?",
         "options": ["true", "false", "null", "0"],
         "correct_option": 1, "explanation": "Instance boolean fields default to `false`."},
        {"id": 9, "topic": "Syntax & Data Types", "difficulty": "Medium",
         "question": "What will `int x = (int) 3.85;` result in?",
         "options": ["4", "3", "Compilation error", "TypeCastException"],
         "correct_option": 1, "explanation": "Narrowing primitive conversion truncates the decimal portion, resulting in 3."},
        {"id": 10, "topic": "Syntax & Data Types", "difficulty": "Hard",
         "question": "Why are String objects immutable in Java?",
         "options": ["Security, string pooling cache efficiency, and thread-safety", "To prevent long variable names", "Due to 16-bit unicode limitations", "They are stored in the CPU registers"],
         "correct_option": 0, "explanation": "String immutability enables string literal pooling, thread-safety, hashcode caching, and security (e.g. file paths, network URLs)."},

        # Operators & Control Flow (5)
        {"id": 11, "topic": "Operators & Control Flow", "difficulty": "Easy",
         "question": "Which logical operator in Java performs short-circuit evaluation for AND?",
         "options": ["&", "&&", "AND", "|"],
         "correct_option": 1, "explanation": "`&&` performs short-circuit logical AND (if the first operand is false, the second is not evaluated)."},
        {"id": 12, "topic": "Operators & Control Flow", "difficulty": "Easy",
         "question": "Which loop executes its body at least once regardless of the condition?",
         "options": ["for loop", "while loop", "do-while loop", "for-each loop"],
         "correct_option": 2, "explanation": "A `do-while` loop evaluates its condition after executing the body, guaranteeing at least one run."},
        {"id": 13, "topic": "Operators & Control Flow", "difficulty": "Medium",
         "question": "What types can be used in a Java `switch` statement expression?",
         "options": ["char, byte, short, int, Character, Byte, Short, Integer, String, or enum", "float, double, and boolean only", "Any arbitrary Object", "Only integers"],
         "correct_option": 0, "explanation": "Java switch supports primitive integers (char, byte, short, int) and their wrappers, String, and enums."},
        {"id": 14, "topic": "Operators & Control Flow", "difficulty": "Medium",
         "question": "What is the ternary operator syntax in Java?",
         "options": ["condition ? expr1 : expr2", "condition -> expr1 : expr2", "if condition then expr1 else expr2", "condition ? expr1 ! expr2"],
         "correct_option": 0, "explanation": "The ternary conditional operator is `condition ? expr1 : expr2`."},
        {"id": 15, "topic": "Operators & Control Flow", "difficulty": "Hard",
         "question": "What will `Integer a = 100; Integer b = 100; System.out.println(a == b);` output?",
         "options": ["true", "false", "NullPointerException", "Compilation error"],
         "correct_option": 0, "explanation": "Java caches Integer objects in the range -128 to 127, so `a == b` compares the same cached reference and prints true."},

        # Methods & Arrays (5)
        {"id": 16, "topic": "Methods & Arrays", "difficulty": "Easy",
         "question": "How do you obtain the number of elements in an array `arr` in Java?",
         "options": ["arr.size()", "arr.length", "arr.length()", "arr.count"],
         "correct_option": 1, "explanation": "Arrays in Java have a built-in read-only public property `length`."},
        {"id": 17, "topic": "Methods & Arrays", "difficulty": "Easy",
         "question": "What is method overloading in Java?",
         "options": ["Methods with the same name but different parameter lists in the same class", "Overriding a superclass method", "Using recursive calls", "Throwing multiple exceptions"],
         "correct_option": 0, "explanation": "Overloading allows multiple methods in the same class with identical names but differing parameter types or counts."},
        {"id": 18, "topic": "Methods & Arrays", "difficulty": "Medium",
         "question": "Is Java pass-by-value or pass-by-reference for method arguments?",
         "options": ["Strictly pass-by-value always", "Strictly pass-by-reference", "Pass-by-value for primitives, pass-by-reference for objects", "Configurable via JVM flag"],
         "correct_option": 0, "explanation": "Java is strictly pass-by-value. For objects, the value of the reference pointer is passed by value."},
        {"id": 19, "topic": "Methods & Arrays", "difficulty": "Medium",
         "question": "What exception is thrown when accessing an index outside of an array's bounds?",
         "options": ["NullPointerException", "ArrayIndexOutOfBoundsException", "IllegalArgumentException", "IndexMismatchException"],
         "correct_option": 1, "explanation": "Java throws `ArrayIndexOutOfBoundsException` on invalid array index access."},
        {"id": 20, "topic": "Methods & Arrays", "difficulty": "Hard",
         "question": "What does `varargs` syntax (`int... nums`) represent in a method parameter?",
         "options": ["A variable treated as an array of integers inside the method", "A dynamic pointer", "An infinite loop", "A thread-safe list"],
         "correct_option": 0, "explanation": "Varargs allows passing 0 or more arguments, treated internally as an array."},

        # OOP: Inheritance & Polymorphism (5)
        {"id": 21, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "Which keyword is used to inherit a class in Java?",
         "options": ["implements", "extends", "inherits", "super"],
         "correct_option": 1, "explanation": "`extends` is used for class inheritance in Java."},
        {"id": 22, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "Does Java support multiple inheritance of classes?",
         "options": ["Yes, using commas", "No, Java supports single class inheritance but multiple interface implementation", "Yes, using the `multi` keyword", "Only for abstract classes"],
         "correct_option": 1, "explanation": "Java classes can only extend a single superclass to avoid the diamond problem, but can implement multiple interfaces."},
        {"id": 23, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "Which keyword refers to the direct superclass constructor or method?",
         "options": ["this", "super", "parent", "base"],
         "correct_option": 1, "explanation": "`super` is used to access superclass members and constructors."},
        {"id": 24, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "What annotation should be used when overriding a superclass method?",
         "options": ["@Override", "@Implement", "@Super", "@Overwrite"],
         "correct_option": 0, "explanation": "`@Override` instructs the compiler to verify that the method actually overrides a superclass method."},
        {"id": 25, "topic": "OOP Concepts", "difficulty": "Hard",
         "question": "What is dynamic method dispatch in Java?",
         "options": ["Resolving an overridden method call at runtime based on the actual object type", "Compiling bytecode on the fly", "Calling static methods via reflection", "Asynchronous method execution"],
         "correct_option": 0, "explanation": "Dynamic method dispatch is runtime polymorphism where the method called is determined by the object's runtime class."},

        # OOP: Interfaces, Abstract Classes & Access Modifiers (5)
        {"id": 26, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "Which access modifier provides the widest visibility in Java?",
         "options": ["private", "default (package-private)", "protected", "public"],
         "correct_option": 3, "explanation": "`public` members are accessible from any other class in any package."},
        {"id": 27, "topic": "OOP Concepts", "difficulty": "Easy",
         "question": "Can an abstract class in Java be instantiated directly with `new`?",
         "options": ["Yes, always", "No, it cannot be instantiated directly", "Only if it has a constructor", "Only inside its own package"],
         "correct_option": 1, "explanation": "Abstract classes cannot be directly instantiated with `new`."},
        {"id": 28, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "What does a `final` keyword indicate when applied to a class?",
         "options": ["The class cannot be instantiated", "The class cannot be subclassed/extended", "All methods are static", "Class is stored in permanent memory"],
         "correct_option": 1, "explanation": "A `final` class cannot be extended by any other class (e.g., `java.lang.String`)."},
        {"id": 29, "topic": "OOP Concepts", "difficulty": "Medium",
         "question": "Since Java 8, what kind of method with an implementation can be added to an interface?",
         "options": ["default method and static method", "abstract method only", "native method only", "synchronized method only"],
         "correct_option": 0, "explanation": "Java 8 introduced `default` and `static` methods with implementations inside interfaces."},
        {"id": 30, "topic": "OOP Concepts", "difficulty": "Hard",
         "question": "What is a Functional Interface in Java?",
         "options": ["An interface with no methods", "An interface with exactly one abstract method", "An interface with only default methods", "A marker interface"],
         "correct_option": 1, "explanation": "A functional interface (annotated with `@FunctionalInterface`) has exactly one abstract method and can be targeted by lambdas."},

        # Collections Framework (5)
        {"id": 31, "topic": "Collections Framework", "difficulty": "Easy",
         "question": "Which root interface does `List`, `Set`, and `Queue` inherit from in `java.util`?",
         "options": ["Map", "Collection", "Iterable", "Array"],
         "correct_option": 1, "explanation": "`List`, `Set`, and `Queue` all extend the `java.util.Collection` interface."},
        {"id": 32, "topic": "Collections Framework", "difficulty": "Easy",
         "question": "Which collection class guarantees NO duplicate elements?",
         "options": ["ArrayList", "LinkedList", "HashSet", "Vector"],
         "correct_option": 2, "explanation": "`Set` implementations like `HashSet` do not permit duplicate elements."},
        {"id": 33, "topic": "Collections Framework", "difficulty": "Medium",
         "question": "What is the internal data structure backing an `ArrayList` in Java?",
         "options": ["Doubly-linked list", "Resizing dynamic array", "Binary Search Tree", "Hash table"],
         "correct_option": 1, "explanation": "`ArrayList` is backed by a dynamically resizable array."},
        {"id": 34, "topic": "Collections Framework", "difficulty": "Medium",
         "question": "What is the key difference between `HashMap` and `Hashtable`?",
         "options": ["`HashMap` is non-synchronized and permits null keys/values; `Hashtable` is synchronized and forbids nulls", "Hashtable is faster", "HashMap does not use hashing", "There is no difference"],
         "correct_option": 0, "explanation": "`HashMap` is unsynchronized and allows one null key and multiple null values, whereas legacy `Hashtable` is thread-safe and rejects nulls."},
        {"id": 35, "topic": "Collections Framework", "difficulty": "Hard",
         "question": "What contract must be maintained when overriding `equals(Object o)` in Java?",
         "options": ["Must also override `hashCode()` such that equal objects produce identical hash codes", "Must make the class final", "Must implement Serializable", "Must return 0 on equality"],
         "correct_option": 0, "explanation": "The equals/hashCode contract dictates that if `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must be true."},

        # Exception Handling (5)
        {"id": 36, "topic": "Exception Handling", "difficulty": "Easy",
         "question": "Which is the root class of all exceptions and errors in Java?",
         "options": ["java.lang.Exception", "java.lang.Throwable", "java.lang.Error", "java.lang.RuntimeException"],
         "correct_option": 1, "explanation": "`java.lang.Throwable` is the superclass of all errors and exceptions in the Java language."},
        {"id": 37, "topic": "Exception Handling", "difficulty": "Easy",
         "question": "Which keyword is used to throw an exception explicitly in Java?",
         "options": ["throws", "throw", "raise", "catch"],
         "correct_option": 1, "explanation": "`throw` throws an exception instance, while `throws` declares checked exceptions in a method signature."},
        {"id": 38, "topic": "Exception Handling", "difficulty": "Medium",
         "question": "What is a Checked Exception in Java?",
         "options": ["Exceptions checked by the compiler and must be either caught or declared in `throws`", "Exceptions that only occur during unit tests", "Subclasses of RuntimeException", "Hardware CPU errors"],
         "correct_option": 0, "explanation": "Checked exceptions (subclasses of Exception excluding RuntimeException) are verified at compile time."},
        {"id": 39, "topic": "Exception Handling", "difficulty": "Medium",
         "question": "What is the purpose of the `try-with-resources` statement introduced in Java 7?",
         "options": ["Allocates CPU resources dynamically", "Automatically closes resources that implement `AutoCloseable` upon completion", "Catching multiple exceptions with bitwise OR", "Managing memory heaps"],
         "correct_option": 1, "explanation": "`try (Resource r = ...) {}` guarantees that every resource implementing `AutoCloseable` is closed at statement exit."},
        {"id": 40, "topic": "Exception Handling", "difficulty": "Hard",
         "question": "Can a `finally` block ever be prevented from executing?",
         "options": ["No, it always runs under every circumstance", "Yes, if `System.exit(0)` is invoked or JVM crashes", "Yes, if an unhandled exception occurs in try", "Yes, if the try block contains a return statement"],
         "correct_option": 1, "explanation": "A finally block executes even if `return` is reached, but will not execute if the JVM halts via `System.exit()` or suffers an abrupt OS crash."},

        # Generics, Streams & Lambdas (5)
        {"id": 41, "topic": "Generics & Streams", "difficulty": "Medium",
         "question": "What is Type Erasure in Java Generics?",
         "options": ["Erasing memory of unused objects", "Compiler removes generic type information after checking, replacing with raw types/bounds in bytecode", "Deleting null generic pointers", "Automatic cast to primitive types"],
         "correct_option": 1, "explanation": "Java generics are implemented via type erasure to maintain backwards compatibility with pre-generic bytecode."},
        {"id": 42, "topic": "Generics & Streams", "difficulty": "Medium",
         "question": "What does `Stream.map()` do in Java 8?",
         "options": ["Filters out unwanted items", "Transforms each element by applying a function to it", "Collects elements into a Map", "Counts total items"],
         "correct_option": 1, "explanation": "`map()` is an intermediate operation that applies a Function to each element, returning a stream of results."},
        {"id": 43, "topic": "Generics & Streams", "difficulty": "Hard",
         "question": "What is the difference between intermediate and terminal operations on a Java Stream?",
         "options": ["Intermediate operations are lazy and return a new Stream; terminal operations trigger execution and return a non-stream result", "Intermediate operations return void", "Terminal operations can be chained", "There is no difference"],
         "correct_option": 0, "explanation": "Intermediate operations (e.g. filter, map) are lazy; execution only commences when a terminal operation (e.g. collect, forEach) is invoked."},
        {"id": 44, "topic": "Generics & Streams", "difficulty": "Hard",
         "question": "What does the wildcard `<? extends Number>` allow in Java Generics?",
         "options": ["Any class that is a superclass of Number", "Any class that is Number or a subclass of Number (Upper Bounded Wildcard)", "Only integers", "Exact Number type only"],
         "correct_option": 1, "explanation": "`? extends T` establishes an upper bound, accepting T or any subtype of T."},
        {"id": 45, "topic": "Generics & Streams", "difficulty": "Hard",
         "question": "What is `Optional<T>` in Java designed to represent?",
         "options": ["Optional method arguments", "A container object which may or may not contain a non-null value, mitigating NullPointerExceptions", "A nullable primitive", "An asynchronous task"],
         "correct_option": 1, "explanation": "`Optional<T>` provides a clear type-level representation of presence or absence of a value."},

        # Multithreading & Concurrency (5)
        {"id": 46, "topic": "Multithreading", "difficulty": "Easy",
         "question": "Which two ways can a thread be created in Java?",
         "options": ["Extending `Thread` class or implementing `Runnable` interface", "Using `ProcessBuilder` or `Runtime`", "Using `Fork` or `Join` keywords", "Creating static functions only"],
         "correct_option": 0, "explanation": "Threads are traditionally created by extending `Thread` or implementing `Runnable`."},
        {"id": 47, "topic": "Multithreading", "difficulty": "Medium",
         "question": "Which method initiates the execution of a thread in Java?",
         "options": ["run()", "start()", "init()", "execute()"],
         "correct_option": 1, "explanation": "`start()` registers and allocates OS thread resources and invokes `run()` asynchronously."},
        {"id": 48, "topic": "Multithreading", "difficulty": "Medium",
         "question": "What does the `synchronized` keyword guarantee in Java?",
         "options": ["Thread executes on a specific CPU core", "Mutual exclusion: only one thread can execute the synchronized block/method on that monitor at a time", "Code executes twice as fast", "No memory is consumed"],
         "correct_option": 1, "explanation": "`synchronized` enforces intrinsic locking, providing mutual exclusion and visibility guarantees."},
        {"id": 49, "topic": "Multithreading", "difficulty": "Hard",
         "question": "What does the `volatile` keyword guarantee for a field in Java?",
         "options": ["Atomic compound operations like `count++`", "Reads and writes go directly to main memory, establishing a happens-before relationship", "Field cannot be modified after constructor", "Field is private to the thread"],
         "correct_option": 1, "explanation": "`volatile` guarantees variable visibility across threads by bypassing CPU thread caches and preventing instruction reordering."},
        {"id": 50, "topic": "Multithreading", "difficulty": "Hard",
         "question": "What package in the standard Java library contains high-level concurrency utilities like `ExecutorService` and `ConcurrentHashMap`?",
         "options": ["java.lang.thread", "java.util.concurrent", "java.io.async", "java.security.thread"],
         "correct_option": 1, "explanation": "`java.util.concurrent` contains production concurrency primitives, thread pools, and atomic variables."}
    ]

    coding = [
        {
            "id": 51,
            "title": "Two Sum Target Finder",
            "skill": "Java",
            "domain": "Algorithms & Problem Solving",
            "topic": "Arrays & Hash Maps",
            "difficulty": "Intermediate",
            "problem_statement": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\nYou can return the answer in any order.",
            "input_format": "Array of integers `nums` and integer `target`.",
            "output_format": "Array of two integer indices `[i, j]`.",
            "constraints": "2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9, -10^9 <= target <= 10^9. Exactly one valid answer exists.",
            "function_name": "twoSum",
            "class_name": "Solution",
            "code_template": """import java.util.*;

public class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your solution here
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
            map.put(nums[i], i);
        }
        return new int[] {-1, -1};
    }
}
""",
            "test_cases": [
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1], "is_hidden": False},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2], "is_hidden": False},
                {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1], "is_hidden": True},
                {"input": {"nums": [1, 5, 8, 12, 19], "target": 20}, "expected": [0, 4], "is_hidden": True}
            ]
        },
        {
            "id": 52,
            "title": "Valid Palindrome String Verifier",
            "skill": "Java",
            "domain": "String Manipulation & Two Pointers",
            "topic": "Strings & Pointers",
            "difficulty": "Intermediate",
            "problem_statement": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.\nGiven a string `s`, return `true` if it is a palindrome, or `false` otherwise.",
            "input_format": "String `s` containing printable ASCII characters.",
            "output_format": "Boolean `true` or `false`.",
            "constraints": "1 <= s.length() <= 2 * 10^5.",
            "function_name": "isPalindrome",
            "class_name": "Solution",
            "code_template": """public class Solution {
    public boolean isPalindrome(String s) {
        // Write your solution here
        int left = 0, right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
""",
            "test_cases": [
                {"input": {"s": "A man, a plan, a canal: Panama"}, "expected": True, "is_hidden": False},
                {"input": {"s": "race a car"}, "expected": False, "is_hidden": False},
                {"input": {"s": " "}, "expected": True, "is_hidden": True},
                {"input": {"s": "0P"}, "expected": False, "is_hidden": True},
                {"input": {"s": "Madam, I'm Adam"}, "expected": True, "is_hidden": True}
            ]
        }
    ]
    return {"mcqs": mcqs, "coding": coding}

def main():
    banks = {
        "Python": create_python_bank(),
        "SQL": create_sql_bank(),
        "Java": create_java_bank()
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(out_dir, "skill_banks.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(banks, f, indent=2)
        
    print(f"Successfully generated skill question banks at {out_file}.")
    for skill, data in banks.items():
        print(f" - {skill}: {len(data['mcqs'])} MCQs, {len(data['coding'])} Coding Challenges")

if __name__ == "__main__":
    main()
