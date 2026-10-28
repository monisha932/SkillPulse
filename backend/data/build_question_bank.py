import json

questions = []

# Domain 1: Python & Core Programming (10 questions)
q1_10 = [
    {
        "id": 1,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Beginner",
        "question": "What will be the output of `bool([])` and `bool([0])` in Python?",
        "options": ["True, True", "False, True", "False, False", "True, False"],
        "correct_option": 1,
        "explanation": "An empty list evaluates to False, while a non-empty list (even containing 0) evaluates to True in Python."
    },
    {
        "id": 2,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Beginner",
        "question": "Which Python built-in function returns both the index and value of items in an iterable?",
        "options": ["zip()", "enumerate()", "map()", "range()"],
        "correct_option": 1,
        "explanation": "enumerate() takes an iterable and returns an enumerate object yielding pairs of (index, item)."
    },
    {
        "id": 3,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "What is the primary difference between a Python list and a tuple?",
        "options": [
            "Lists are immutable; tuples are mutable",
            "Lists are mutable; tuples are immutable",
            "Tuples cannot store heterogeneous types",
            "Lists have fixed size, while tuples are dynamic"
        ],
        "correct_option": 1,
        "explanation": "Lists can be modified after creation (mutable), whereas tuples cannot be changed once initialized (immutable)."
    },
    {
        "id": 4,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "In Python, what is the purpose of the `__init__` method in a class?",
        "options": [
            "To destroy an existing object instance",
            "To initialize the instance attributes when an object is created",
            "To allocate raw memory from the heap",
            "To define class-level static variables"
        ],
        "correct_option": 1,
        "explanation": "__init__ is the constructor method in Python classes, invoked automatically to initialize instance state."
    },
    {
        "id": 5,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "What does a Python generator function use to produce values lazily one at a time?",
        "options": ["return", "yield", "emit", "await"],
        "correct_option": 1,
        "explanation": "The `yield` statement suspends execution and returns an intermediate value, resuming on the next `next()` call."
    },
    {
        "id": 6,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "What is the purpose of Python's Global Interpreter Lock (GIL)?",
        "options": [
            "Preventing multithreaded I/O operations",
            "Ensuring only one native thread executes Python bytecode at a time in CPython",
            "Encrypting source code during compilation",
            "Locking file writes in multi-process applications"
        ],
        "correct_option": 1,
        "explanation": "CPython's GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes simultaneously."
    },
    {
        "id": 7,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Advanced",
        "question": "What will `a = [1, 2, 3]; b = a; b.append(4); print(len(a))` output?",
        "options": ["3", "4", "Error", "None"],
        "correct_option": 1,
        "explanation": "In Python, variable assignment creates a reference to the same object in memory. Modifying `b` mutates `a`."
    },
    {
        "id": 8,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Advanced",
        "question": "What is the time complexity of searching for a key in a standard Python dictionary with N items on average?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
        "correct_option": 0,
        "explanation": "Python dictionaries are implemented using hash tables, offering average O(1) time complexity for lookups."
    },
    {
        "id": 9,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "Which module in Python is standard for working with regular expressions?",
        "options": ["regex_std", "re", "strings", "pattern"],
        "correct_option": 1,
        "explanation": "The standard library module `re` provides regular expression matching operations in Python."
    },
    {
        "id": 10,
        "domain": "Python & Core Programming",
        "skill": "Python",
        "difficulty": "Intermediate",
        "question": "What does the `*args` syntax signify in a Python function signature?",
        "options": [
            "Arbitrary keyword arguments as a dictionary",
            "Arbitrary positional arguments packed into a tuple",
            "Pointer dereferencing for C extensions",
            "Mandatory default parameter assignments"
        ],
        "correct_option": 1,
        "explanation": "*args allows passing a variable number of positional arguments to a function, accessible as a tuple."
    }
]
questions.extend(q1_10)

# Domain 2: Data Structures & Algorithms (10 questions)
q11_20 = [
    {
        "id": 11,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Beginner",
        "question": "Which data structure operates on a First-In-First-Out (FIFO) principle?",
        "options": ["Stack", "Queue", "Binary Tree", "Heap"],
        "correct_option": 1,
        "explanation": "A Queue follows the FIFO rule, where elements are inserted at the rear and removed from the front."
    },
    {
        "id": 12,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Beginner",
        "question": "What is the worst-case time complexity of QuickSort when a poor pivot is consistently chosen?",
        "options": ["O(N log N)", "O(N)", "O(N^2)", "O(2^N)"],
        "correct_option": 2,
        "explanation": "When the chosen pivot is always the smallest or greatest element, QuickSort degrades to O(N^2)."
    },
    {
        "id": 13,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Intermediate",
        "question": "In a balanced Binary Search Tree (such as an AVL tree) with N nodes, what is the search time complexity?",
        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
        "correct_option": 1,
        "explanation": "In a balanced BST, tree height is bounded by O(log N), giving O(log N) lookup, insertion, and deletion."
    },
    {
        "id": 14,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Intermediate",
        "question": "Which graph traversal algorithm uses a Queue and visits nodes level by level?",
        "options": ["Depth-First Search (DFS)", "Breadth-First Search (BFS)", "Dijkstra's Algorithm", "Bellman-Ford"],
        "correct_option": 1,
        "explanation": "BFS uses a queue to explore all neighbors of a node before moving down to subsequent depths."
    },
    {
        "id": 15,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Intermediate",
        "question": "Which algorithmic paradigm breaks a problem into smaller overlapping subproblems and stores their solutions?",
        "options": ["Greedy Method", "Divide and Conquer", "Dynamic Programming", "Backtracking"],
        "correct_option": 2,
        "explanation": "Dynamic Programming optimizes recursive problems by caching solutions to overlapping subproblems (memoization/tabulation)."
    },
    {
        "id": 16,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Intermediate",
        "question": "What data structure is typically used to implement a priority queue efficiently?",
        "options": ["Singly Linked List", "Binary Heap", "Circular Array", "Hash Map"],
        "correct_option": 1,
        "explanation": "A Binary Heap (Min/Max Heap) provides O(log N) insertion and O(log N) extraction of the priority element."
    },
    {
        "id": 17,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Intermediate",
        "question": "What is the average time complexity to insert an element at the head of a Singly Linked List?",
        "options": ["O(1)", "O(N)", "O(log N)", "O(N^2)"],
        "correct_option": 0,
        "explanation": "Inserting at the head requires creating a node and re-pointing the head pointer, taking constant O(1) time."
    },
    {
        "id": 18,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Advanced",
        "question": "Which algorithm is guaranteed to find the shortest path in a weighted graph with non-negative edge weights?",
        "options": ["Kruskal's Algorithm", "Dijkstra's Algorithm", "Tarjan's Algorithm", "Floyd-Warshall for negative cycles"],
        "correct_option": 1,
        "explanation": "Dijkstra's algorithm greedily finds the single-source shortest path in graphs with non-negative weights."
    },
    {
        "id": 19,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Advanced",
        "question": "What technique is used to resolve collisions in hash tables by storing colliding elements in linked lists?",
        "options": ["Linear Probing", "Separate Chaining", "Double Hashing", "Quadratic Probing"],
        "correct_option": 1,
        "explanation": "Separate chaining resolves hash collisions by maintaining a bucket chain (linked list or tree) at each hash slot."
    },
    {
        "id": 20,
        "domain": "Data Structures & Algorithms",
        "skill": "Algorithms",
        "difficulty": "Advanced",
        "question": "What is the space complexity of a recursive Depth-First Search on a tree of maximum depth H?",
        "options": ["O(1)", "O(H)", "O(N^2)", "O(2^H)"],
        "correct_option": 1,
        "explanation": "Recursive DFS consumes call stack frames proportional to the maximum recursion depth, which is O(H)."
    }
]
questions.extend(q11_20)

# Domain 3: Web Development & APIs (10 questions)
q21_30 = [
    {
        "id": 21,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Beginner",
        "question": "Which HTTP status code signifies that a requested resource was not found on the server?",
        "options": ["200 OK", "301 Moved Permanently", "404 Not Found", "500 Internal Server Error"],
        "correct_option": 2,
        "explanation": "HTTP 404 indicates the origin server did not find a current representation for the target resource."
    },
    {
        "id": 22,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Beginner",
        "question": "Which HTTP method should be idempotent and used to retrieve representation of a resource without side effects?",
        "options": ["POST", "GET", "PATCH", "CONNECT"],
        "correct_option": 1,
        "explanation": "GET requests are safe and idempotent; they should only retrieve data without altering server state."
    },
    {
        "id": 23,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Intermediate",
        "question": "What does CORS stand for in modern browser security architecture?",
        "options": [
            "Central Object Relational Storage",
            "Cross-Origin Resource Sharing",
            "Client Origin Request System",
            "Cryptographic Open Routing Standard"
        ],
        "correct_option": 1,
        "explanation": "CORS (Cross-Origin Resource Sharing) is an HTTP-header based security mechanism enabling controlled resource access across domains."
    },
    {
        "id": 24,
        "domain": "Web Development & APIs",
        "skill": "JavaScript",
        "difficulty": "Intermediate",
        "question": "What is the primary role of the JavaScript Event Loop?",
        "options": [
            "Compile JavaScript code into native machine assembly",
            "Monitor call stack and task queue to orchestrate non-blocking asynchronous execution",
            "Manage hardware multi-core CPU scheduling",
            "Run garbage collection synchronously during paint cycles"
        ],
        "correct_option": 1,
        "explanation": "The Event Loop continuously checks if the call stack is empty, pushing tasks from microtask/macrotask queues onto the stack."
    },
    {
        "id": 25,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Intermediate",
        "question": "What is the structure of a JSON Web Token (JWT)?",
        "options": [
            "Prefix.Payload.Timestamp",
            "Header.Payload.Signature",
            "PublicKey.Ciphertext.Nonce",
            "User.Roles.Permissions"
        ],
        "correct_option": 1,
        "explanation": "A JWT consists of three Base64URL-encoded parts separated by dots: Header, Payload, and Signature."
    },
    {
        "id": 26,
        "domain": "Web Development & APIs",
        "skill": "JavaScript",
        "difficulty": "Intermediate",
        "question": "What will `typeof NaN` return in standard JavaScript?",
        "options": ["'undefined'", "'nan'", "'number'", "'object'"],
        "correct_option": 2,
        "explanation": "In JavaScript specification (IEEE 754 float), NaN (Not a Number) is classified under the 'number' type."
    },
    {
        "id": 27,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Intermediate",
        "question": "In REST architectural style, which HTTP method is typically used for partial updates of an existing resource?",
        "options": ["PUT", "PATCH", "POST", "UPDATE"],
        "correct_option": 1,
        "explanation": "PATCH is applied to modify partial resources, whereas PUT conventionally replaces the entire representation."
    },
    {
        "id": 28,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Advanced",
        "question": "What security vulnerability is mitigated by setting the `HttpOnly` flag on session cookies?",
        "options": [
            "SQL Injection (SQLi)",
            "Cross-Site Scripting (XSS) token theft",
            "Cross-Site Request Forgery (CSRF)",
            "Distributed Denial of Service (DDoS)"
        ],
        "correct_option": 1,
        "explanation": "HttpOnly cookies cannot be accessed by client-side scripts via `document.cookie`, preventing XSS attacks from reading session tokens."
    },
    {
        "id": 29,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Advanced",
        "question": "What is the main advantage of WebSockets over traditional HTTP polling?",
        "options": [
            "Automatic encryption without TLS",
            "Full-duplex, persistent bidirectional communication with minimal header overhead",
            "Enforces strict relational ACID transactions",
            "Guarantees delivery over unreliable UDP connections"
        ],
        "correct_option": 1,
        "explanation": "WebSockets maintain a persistent TCP connection allowing simultaneous bidirectional messaging with tiny frame overhead."
    },
    {
        "id": 30,
        "domain": "Web Development & APIs",
        "skill": "Web Development",
        "difficulty": "Intermediate",
        "question": "Which CSS layout model is optimized for one-dimensional layouts (either rows or columns)?",
        "options": ["CSS Grid", "Flexbox", "Float", "Table Layout"],
        "correct_option": 1,
        "explanation": "Flexbox (Flexible Box Layout) is designed specifically for 1-dimensional layouts, while CSS Grid handles 2 dimensions."
    }
]
questions.extend(q21_30)

# Domain 4: Databases & SQL (10 questions)
q31_40 = [
    {
        "id": 31,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Beginner",
        "question": "Which SQL clause is used to filter records resulting from an aggregate function like SUM or COUNT?",
        "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
        "correct_option": 1,
        "explanation": "The HAVING clause was added to SQL because the WHERE keyword cannot be used with aggregate functions."
    },
    {
        "id": 32,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Beginner",
        "question": "What does the 'ACID' acronym stand for in relational database management systems?",
        "options": [
            "Authentication, Concurrency, Integrity, Durability",
            "Atomicity, Consistency, Isolation, Durability",
            "Access, Control, Indexing, Distribution",
            "Aggregation, Consistency, Inheritance, Data"
        ],
        "correct_option": 1,
        "explanation": "ACID properties ensure reliable processing of database transactions: Atomicity, Consistency, Isolation, Durability."
    },
    {
        "id": 33,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Intermediate",
        "question": "Which type of SQL JOIN returns all records from the left table and matched records from the right table?",
        "options": ["INNER JOIN", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN"],
        "correct_option": 1,
        "explanation": "A LEFT JOIN returns all rows from the left table, with NULL for right-table columns if no match is found."
    },
    {
        "id": 34,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Intermediate",
        "question": "What is the primary purpose of a database Index (e.g., B-Tree index)?",
        "options": [
            "Encrypt sensitive column values",
            "Accelerate query retrieval speed at the cost of additional storage and write overhead",
            "Enforce foreign key constraints across different database servers",
            "Automatically normalize tables into 3rd Normal Form"
        ],
        "correct_option": 1,
        "explanation": "Indexes speed up SELECT queries by providing logarithmic search paths, though they add overhead to INSERT/UPDATE operations."
    },
    {
        "id": 35,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Intermediate",
        "question": "What database normalization form eliminates transitive dependencies between non-key attributes?",
        "options": ["1NF", "2NF", "3NF", "BCNF"],
        "correct_option": 2,
        "explanation": "Third Normal Form (3NF) requires a table to be in 2NF and have no transitive functional dependencies."
    },
    {
        "id": 36,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Intermediate",
        "question": "What happens during a transaction ROLLBACK in a relational database?",
        "options": [
            "All pending modifications in the current transaction are permanently committed",
            "All uncommitted modifications made during the transaction are discarded, restoring prior state",
            "The database drops the modified table schemas",
            "A backup dump file is restored from cloud storage"
        ],
        "correct_option": 1,
        "explanation": "ROLLBACK reverts all state changes made within the current transaction block, preserving atomicity."
    },
    {
        "id": 37,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Advanced",
        "question": "Which database isolation level completely prevents Dirty Reads, Non-repeatable Reads, and Phantom Reads?",
        "options": ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable"],
        "correct_option": 3,
        "explanation": "Serializable is the highest ANSI SQL isolation level, emulating strictly serial execution and preventing all three anomalies."
    },
    {
        "id": 38,
        "domain": "Databases & SQL",
        "skill": "Databases",
        "difficulty": "Intermediate",
        "question": "What is a primary operational characteristic of NoSQL document stores (like MongoDB) compared to traditional RDBMS?",
        "options": [
            "Strict schema enforcement across all rows",
            "Dynamic/schemaless JSON-like document storage supporting flexible hierarchical data models",
            "Lack of indexing mechanisms",
            "Native execution of SQL-92 statements"
        ],
        "correct_option": 1,
        "explanation": "Document databases store semi-structured data in flexible BSON/JSON formats without predefined table schemas."
    },
    {
        "id": 39,
        "domain": "Databases & SQL",
        "skill": "SQL",
        "difficulty": "Advanced",
        "question": "What SQL construct allows computing running totals or rankings across partitioned sets of rows without collapsing them?",
        "options": ["Window Functions (e.g., OVER (PARTITION BY ...))", "GROUP BY with HAVING", "UNION ALL", "CROSS JOIN"],
        "correct_option": 0,
        "explanation": "Window functions perform calculations across related row sets while preserving the individual row identities."
    },
    {
        "id": 40,
        "domain": "Databases & SQL",
        "skill": "Databases",
        "difficulty": "Intermediate",
        "question": "What is Connection Pooling in database client architectures?",
        "options": [
            "Merging multiple SQL queries into one single network packet",
            "Maintaining a cache of open database connections for reuse to eliminate connection creation overhead",
            "Replicating tables across geographical zones",
            "Automatic load balancing of DNS queries"
        ],
        "correct_option": 1,
        "explanation": "Connection pooling reuses active physical connections instead of opening/closing sockets on every request."
    }
]
questions.extend(q31_40)

# Domain 5: Cloud, DevOps & System Architecture (10 questions)
q41_50 = [
    {
        "id": 41,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "DevOps",
        "difficulty": "Beginner",
        "question": "What is the primary benefit of containerization with Docker compared to traditional Virtual Machines?",
        "options": [
            "Containers bundle a full guest OS kernel, consuming more disk space",
            "Containers share the host OS kernel and isolate at process level, being much lighter and faster to start",
            "Docker eliminates the need for networking protocols",
            "Containers can only run on single-core architectures"
        ],
        "correct_option": 1,
        "explanation": "Docker containers share the host kernel and isolate processes via cgroups/namespaces, enabling lightweight, rapid spin-ups."
    },
    {
        "id": 42,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "DevOps",
        "difficulty": "Intermediate",
        "question": "What does CI/CD stand for in modern software engineering workflows?",
        "options": [
            "Continuous Integration and Continuous Deployment / Delivery",
            "Central Interface and Client Distribution",
            "Code Inspection and Cloud Debugging",
            "Cryptographic Integrity and Cyber Defense"
        ],
        "correct_option": 0,
        "explanation": "CI/CD automates code testing, building, and delivery pipelines to release software rapidly and reliably."
    },
    {
        "id": 43,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "Cloud",
        "difficulty": "Intermediate",
        "question": "What is the core concept of Infrastructure as Code (IaC) tools like Terraform?",
        "options": [
            "Manually clicking web console options to configure servers",
            "Defining and provisioning cloud infrastructure using declarative configuration files versioned in Git",
            "Compiling application binaries directly into bare metal",
            "Automated unit test generation for frontend code"
        ],
        "correct_option": 1,
        "explanation": "IaC defines computing resources declaratively in human-readable configuration files for reproducible deployments."
    },
    {
        "id": 44,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "System Design",
        "difficulty": "Intermediate",
        "question": "What is a Reverse Proxy commonly used for in production web architectures?",
        "options": [
            "Scanning local hard drives for malware",
            "Load balancing incoming client requests, SSL termination, and caching static assets before backend servers",
            "Converting relational SQL tables to NoSQL graphs",
            "Intercepting client outgoing DNS requests"
        ],
        "correct_option": 1,
        "explanation": "Reverse proxies (like Nginx/Envoy) route incoming traffic, balance loads, handle TLS decryption, and protect internal servers."
    },
    {
        "id": 45,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "System Design",
        "difficulty": "Advanced",
        "question": "According to the CAP theorem, what three guarantees can a distributed data store choose between (at most two simultaneously)?",
        "options": [
            "Concurrency, Accuracy, Persistence",
            "Consistency, Availability, Partition Tolerance",
            "Capacity, Agility, Performance",
            "Caching, Authentication, Parity"
        ],
        "correct_option": 1,
        "explanation": "The CAP theorem states that a distributed system can simultaneously provide at most two out of Consistency, Availability, and Partition Tolerance."
    },
    {
        "id": 46,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "Cloud",
        "difficulty": "Intermediate",
        "question": "Which cloud computing model executes code on-demand in response to events without managing server provisioning?",
        "options": ["IaaS (Infrastructure as a Service)", "Serverless / FaaS (Function as a Service)", "Bare-metal Colocation", "PaaS without autoscaling"],
        "correct_option": 1,
        "explanation": "Serverless / FaaS (e.g. AWS Lambda, Google Cloud Functions) runs code stateless on event triggers with automatic scaling."
    },
    {
        "id": 47,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "System Design",
        "difficulty": "Intermediate",
        "question": "Why is an in-memory cache like Redis used in front of relational databases?",
        "options": [
            "To replace disk-based relational storage permanently",
            "To provide sub-millisecond read access for frequently requested or computed data, reducing DB query load",
            "To automatically format frontend CSS stylesheets",
            "To enforce strict foreign key constraints"
        ],
        "correct_option": 1,
        "explanation": "In-memory stores serve reads in RAM with microsecond latencies, drastically reducing database load and latency."
    },
    {
        "id": 48,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "DevOps",
        "difficulty": "Intermediate",
        "question": "In Kubernetes, what is the smallest deployable computing unit that can be created and managed?",
        "options": ["Pod", "Cluster", "Node", "Ingress"],
        "correct_option": 0,
        "explanation": "A Pod encapsulates one or more containers, shared storage resources, and network identities in Kubernetes."
    },
    {
        "id": 49,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "System Design",
        "difficulty": "Advanced",
        "question": "What is the purpose of the Circuit Breaker pattern in microservices architecture?",
        "options": [
            "Instantly shut down the entire cluster when CPU reaches 50%",
            "Detect failures and encapsulate the logic of preventing a failure from constantly cascading during maintenance or outages",
            "Encrypt network traffic between microservices",
            "Automate database schema migrations"
        ],
        "correct_option": 1,
        "explanation": "A circuit breaker prevents repeated calls to failing downstream services, allowing them time to recover without crashing callers."
    },
    {
        "id": 50,
        "domain": "Cloud, DevOps & System Architecture",
        "skill": "System Design",
        "difficulty": "Intermediate",
        "question": "What is horizontal scaling (scaling out) as opposed to vertical scaling (scaling up)?",
        "options": [
            "Adding more RAM/CPU cores to an existing single machine",
            "Adding more server instances or nodes to distribute workload across a cluster",
            "Upgrading the operating system kernel version",
            "Converting synchronous code to multithreaded code"
        ],
        "correct_option": 1,
        "explanation": "Horizontal scaling adds more instances/machines to distribute traffic, whereas vertical scaling upgrades the resources of a single machine."
    }
]
questions.extend(q41_50)

# Programming Questions (2 Questions with Test Suites)
coding_questions = [
    {
        "id": 51,
        "domain": "Algorithms & Problem Solving",
        "skill": "Problem Solving",
        "difficulty": "Intermediate",
        "title": "Subarray Target Sum Locator",
        "problem_statement": (
            "Given an integer array `nums` and an integer `target`, return the 0-based start and end indices "
            "[start, end] of a contiguous non-empty subarray that sums to `target`.\n"
            "If multiple subarrays exist, return the first one found.\n"
            "If no such subarray exists, return `[-1, -1]`.\n\n"
            "Example 1:\nInput: nums = [1, 2, 3, 7, 5], target = 12\nOutput: [1, 3]  (Since 2 + 3 + 7 = 12)\n\n"
            "Example 2:\nInput: nums = [1, 2, 3, 4, 5], target = 100\nOutput: [-1, -1]"
        ),
        "language": "python",
        "function_name": "find_target_subarray",
        "code_template": (
            "def find_target_subarray(nums: list, target: int) -> list:\n"
            "    # Write your solution here\n"
            "    # Return [start_index, end_index] or [-1, -1]\n"
            "    pass\n"
        ),
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
        "domain": "Algorithms & Problem Solving",
        "skill": "Problem Solving",
        "difficulty": "Intermediate",
        "title": "Valid Bracket Sequence Validator",
        "problem_statement": (
            "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid.\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type.\n\n"
            "Example 1:\nInput: s = \"()[]{}\"\nOutput: True\n\n"
            "Example 2:\nInput: s = \"(]\"\nOutput: False\n\n"
            "Example 3:\nInput: s = \"([{}])\"\nOutput: True"
        ),
        "language": "python",
        "function_name": "is_valid_brackets",
        "code_template": (
            "def is_valid_brackets(s: str) -> bool:\n"
            "    # Write your solution here\n"
            "    # Return True if valid, False otherwise\n"
            "    pass\n"
        ),
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

payload = {
    "total_mcqs": len(questions),
    "total_coding": len(coding_questions),
    "mcq_questions": questions,
    "coding_questions": coding_questions
}

with open("backend/data/question_bank.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print(f"Successfully generated question_bank.json with {len(questions)} MCQs and {len(coding_questions)} Coding Questions.")
