import json
import math
from typing import Dict, Any, List, Optional
from backend.database import get_db_connection
from backend.services.gap_engine import calculate_skill_gaps

# Comprehensive Knowledge Catalog for Micro-Credential Curriculum Modules
# Defines rich, non-generic engineering curriculum details for tech competencies
MODULE_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "advanced sql": {
        "title": "Advanced SQL & Query Optimization",
        "category": "Database / Querying",
        "default_hours": 12,
        "difficulty": "Advanced",
        "learning_objective": "Master advanced SQL analytic functions, subquery optimization, indexing strategies, and complex window operations for high-throughput relational databases.",
        "prerequisites": [],
        "topics": [
            "Window Functions: ROW_NUMBER, RANK, DENSE_RANK, NTILE, and Moving Averages",
            "Common Table Expressions (CTEs) & Recursive Query Architectures",
            "Index Types: B-Trees, Hash Indexes, Composite Indexes, and Query Execution Plans (EXPLAIN ANALYZE)",
            "Query Optimization: Avoiding Full Table Scans, SARGable Predicates, and Join Algorithms",
            "ACID Transactions, Isolation Levels (Read Committed, Serializable), and Concurrency Control"
        ],
        "learning_resources": [
            {"title": "PostgreSQL Official Documentation: Window Functions", "type": "Documentation", "url": "https://www.postgresql.org/docs/current/tutorial-window.html"},
            {"title": "Use The Index, Luke: A Guide to Database Performance", "type": "Guide", "url": "https://use-the-index-luke.com/"},
            {"title": "SQL Performance Explained by Markus Winand", "type": "Technical Reference", "url": "https://sql-performance-explained.com/"}
        ],
        "practice_activities": [
            "Write sliding window aggregates to calculate 7-day trailing revenue in an e-commerce transaction dataset",
            "Profile and optimize a slow 5-table JOIN query using EXPLAIN ANALYZE to reduce execution cost by >60%",
            "Implement a recursive CTE to traverse hierarchical organizational reporting trees"
        ],
        "assessment": "15 Advanced MCQ scenario questions on indexing strategies & execution plans + 1 complex query optimization challenge.",
        "project_task": "Build and tune a high-throughput financial ledger reporting schema capable of sub-100ms analytical summaries over 500,000 transaction records."
    },
    "statistics": {
        "title": "Applied Statistical Inference & Exploratory Modeling",
        "category": "Mathematics & Modeling",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Apply inferential statistics, probability distributions, hypothesis testing, and regression analysis to extract validated insights from empirical business datasets.",
        "prerequisites": [],
        "topics": [
            "Descriptive Statistics: Central Tendency, Dispersion, Skewness, Kurtosis, and Interquartile Ranges",
            "Probability Distributions: Normal, Binomial, Poisson, and Central Limit Theorem",
            "Hypothesis Testing: Null/Alternative Hypotheses, P-values, Z-tests, Two-sample T-tests, and Chi-Square",
            "Confidence Intervals, Statistical Significance, and Type I / Type II Error Mitigation",
            "Bivariate Analysis: Pearson/Spearman Correlation and Ordinary Least Squares (OLS) Linear Regression"
        ],
        "learning_resources": [
            {"title": "OpenIntro Statistics (Free Textbook)", "type": "Textbook", "url": "https://www.openintro.org/book/os/"},
            {"title": "Khan Academy: Advanced Probability and Statistics", "type": "Interactive Course", "url": "https://www.khanacademy.org/math/statistics-probability"},
            {"title": "NIST Engineering Statistics Handbook", "type": "Handbook", "url": "https://www.itl.nist.gov/div898/handbook/"}
        ],
        "practice_activities": [
            "Perform two-sample hypothesis testing on A/B conversion experiment data to evaluate statistical significance at α = 0.05",
            "Calculate confidence intervals for customer lifetime value across market segments",
            "Diagnose collinearity and fit an OLS regression model predicting product churn"
        ],
        "assessment": "20 Statistics problem-solving questions testing hypothesis selection, p-value interpretation, and regression analysis.",
        "project_task": "Deliver an empirical statistical evaluation report on customer cohort retention, validating A/B test lift with rigorous confidence intervals."
    },
    "python for data analysis": {
        "title": "Python for Data Analysis & Scripting",
        "category": "Programming & Scripting",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Harness modern Python programming, NumPy vectorized numerical arrays, file ingestion, and robust data pipelines for scalable automated analysis.",
        "prerequisites": [],
        "topics": [
            "Python Idiomatic Scripting: List/Dict Comprehensions, Lambda Functions, and Generator Expressions",
            "NumPy Vectorized Operations: Broadcasting, N-dimensional Arrays, Boolean Masking, and Linear Algebra",
            "File I/O and Ingestion: Parsing CSV, Parquet, JSON, and Connecting to SQL Engines via SQLAlchemy",
            "Error Handling, Logging, and Clean Code Principles for Data Automation Pipelines",
            "Virtual Environments, Package Management (Poetry/Pip), and Jupyter Notebook Workflows"
        ],
        "learning_resources": [
            {"title": "Python for Data Analysis (3rd Edition) by Wes McKinney", "type": "Book", "url": "https://wesmckinney.com/book/"},
            {"title": "Official Python 3 Documentation & Standard Library", "type": "Documentation", "url": "https://docs.python.org/3/"},
            {"title": "NumPy User Guide & Vectorization Best Practices", "type": "Documentation", "url": "https://numpy.org/doc/stable/user/"}
        ],
        "practice_activities": [
            "Vectorize matrix normalization calculations using NumPy broadcasting without explicit Python loops",
            "Construct an automated ingestion script that downloads, cleans, and merges multiple weekly CSV logs",
            "Build robust exception-handling wrappers around external database connections"
        ],
        "assessment": "15 Python MCQs + 1 live data ingestion scripting exercise passing automated test cases.",
        "project_task": "Engineer an automated data extraction and normalization pipeline that converts raw semi-structured JSON telemetry into clean analytical records."
    },
    "pandas": {
        "title": "Data Wrangling & Manipulation with Pandas",
        "category": "Data Wrangling & Manipulation",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Perform high-performance data transformations, multi-index aggregation, missing data imputation, and tidy data reshaping using the Pandas library.",
        "prerequisites": ["Python for Data Analysis", "Python Data Structures"],
        "topics": [
            "Series and DataFrame Structures: Indexing (.loc, .iloc), Filtering, and Memory-Efficient Dtypes",
            "Data Cleansing: Handling Missing Values (dropna, fillna, interpolate) and Duplicate Resolution",
            "Groupby Operations, Split-Apply-Combine Pattern, and Named Aggregations",
            "Reshaping & Restructuring: Melt, Pivot Tables, Stacking, and Categorical Encoding",
            "Time-Series Analysis: DatetimeIndex, Resampling, Window Rolling Calculations, and Timezone Handling"
        ],
        "learning_resources": [
            {"title": "Pandas Official Documentation & API Reference", "type": "Documentation", "url": "https://pandas.pydata.org/docs/"},
            {"title": "Modern Pandas by Tom Augspurger", "type": "Guide", "url": "https://tomaugspurger.net/posts/modern-1-intro/"},
            {"title": "Data Carpentry: Data Analysis and Visualization in Python", "type": "Course", "url": "https://datacarpentry.org/python-ecology-lesson/"}
        ],
        "practice_activities": [
            "Clean a messy 100,000-row dataset containing missing values, irregular dates, and corrupted string currencies",
            "Compute monthly rolling metrics and cumulative revenue per customer cohort using groupby and transform",
            "Pivot and unpivot multi-category quarterly performance surveys into tidy analytics tables"
        ],
        "assessment": "15 Pandas MCQs + 1 hands-on DataFrame manipulation challenge validating correct aggregations.",
        "project_task": "Construct a multi-source ETL cleansing pipeline in Pandas that standardizes disparate regional sales logs into a unified analytics data frame."
    },
    "data visualization": {
        "title": "Visual Analytics & Exploratory Storytelling",
        "category": "Visual Analytics",
        "default_hours": 8,
        "difficulty": "Intermediate",
        "learning_objective": "Communicate complex quantitative patterns clearly using visual grammar, Matplotlib, Seaborn, interactive Plotly charts, and cognitive design standards.",
        "prerequisites": ["Pandas", "Statistics"],
        "topics": [
            "Grammar of Graphics & Cognitive Visual Principles: Color Theory, Contrast, and Chart Junk Elimination",
            "Distribution & Trend Plotting with Seaborn: Histograms, KDEs, Box Plots, and Violin Plots",
            "Relational Visualizations: Scatter Plots, Pairplots, Heatmaps, and FacetGrids",
            "Interactive Web Visualizations: Plotly Express, Tooltips, Zooming, and Hover Metadata",
            "Executive Dashboard Storytelling: Guiding Attention, Annotations, and KPI Callouts"
        ],
        "learning_resources": [
            {"title": "Storytelling with Data by Cole Nussbaumer Knaflic", "type": "Book", "url": "https://www.storytellingwithdata.com/"},
            {"title": "Seaborn: Statistical Data Visualization Documentation", "type": "Documentation", "url": "https://seaborn.pydata.org/"},
            {"title": "Plotly Python Open Source Graphing Library", "type": "Documentation", "url": "https://plotly.com/python/"}
        ],
        "practice_activities": [
            "Design an annotated heatmap displaying cross-feature correlations and significance thresholds",
            "Build an interactive Plotly scatter plot with slider-based temporal filtering across product lines",
            "Redesign an overcrowded bar chart into an executive-ready visual insight with clear narrative callouts"
        ],
        "assessment": "15 Visual design & interpretation MCQs + 1 exploratory chart generation assignment.",
        "project_task": "Produce an executive visual analytics story deck evaluating user conversion funnels, complete with interactive Plotly diagnostic charts."
    },
    "power bi": {
        "title": "Business Intelligence Dashboards & DAX Modeling with Power BI",
        "category": "Business Intelligence Tools",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Architect enterprise semantic data models, author sophisticated DAX measures, and publish automated interactive Power BI business intelligence dashboards.",
        "prerequisites": ["Advanced SQL", "Data Visualization"],
        "topics": [
            "Power Query Ingestion: M Code Transformations, Schema Shaping, and Automated Scheduled Refreshes",
            "Star Schema Architecture: Fact Tables, Dimension Tables, Role-Playing Dimensions, and Relationships",
            "DAX Fundamentals: Calculated Columns vs Measures, Implicit vs Explicit Measures",
            "Advanced DAX: CALCULATE, FILTER, ALL, ALLSELECTED, Time Intelligence (YTD, QTD, MoM Growth)",
            "Dashboard UX: Drill-through Filters, Bookmarks, Row-Level Security (RLS), and Mobile Layouts"
        ],
        "learning_resources": [
            {"title": "Microsoft Power BI Official Documentation & Learning Paths", "type": "Documentation", "url": "https://learn.microsoft.com/en-us/power-bi/"},
            {"title": "SQLBI: DAX Patterns and Advanced Calculations", "type": "Guide", "url": "https://www.daxpatterns.com/"},
            {"title": "Enterprise DNA Power BI Best Practices", "type": "Technical Resource", "url": "https://enterprisedna.co/"}
        ],
        "practice_activities": [
            "Model an e-commerce Star Schema with 1 Fact table and 4 Dimension tables, resolving many-to-many pitfalls",
            "Author DAX measures calculating Year-over-Year (YoY) revenue percentage growth and customer churn rate",
            "Configure role-level security (RLS) restricting regional sales managers to their respective territories"
        ],
        "assessment": "20 Power BI and DAX modeling MCQs + 1 semantic model calculation exercise.",
        "project_task": "Build an end-to-end interactive Enterprise Executive Dashboard in Power BI with dynamic DAX time-intelligence KPIs and drill-down capabilities."
    },
    "javascript": {
        "title": "Modern JavaScript & Asynchronous Web Engineering",
        "category": "Frontend / Language",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Master ECMAScript 6+, prototype inheritance, closures, the browser event loop, Promises, and async/await for scalable frontend web applications.",
        "prerequisites": ["HTML/CSS"],
        "topics": [
            "ES6+ Language Features: Destructuring, Spread/Rest, Modules, Symbols, and Optional Chaining",
            "Execution Context, Call Stack, Scope Chains, Closures, and Variable Hoisting",
            "Asynchronous JavaScript: The Browser Event Loop, Microtask Queue, Promises, and async/await",
            "DOM Manipulation, Event Bubbling/Capturing, Delegation, and Browser Performance",
            "Fetch API, WebSockets, JSON Serialization, and Client-side State Management"
        ],
        "learning_resources": [
            {"title": "MDN Web Docs: JavaScript Guide & Reference", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
            {"title": "JavaScript.info: The Modern JavaScript Tutorial", "type": "Interactive Guide", "url": "https://javascript.info/"},
            {"title": "You Don't Know JS Yet by Kyle Simpson", "type": "Book", "url": "https://github.com/getify/You-Dont-Know-JS"}
        ],
        "practice_activities": [
            "Implement a debounced search input component using closures and asynchronous Fetch API",
            "Write a Promise-based concurrency throttle queue handling multiple simultaneous HTTP requests",
            "Trace and debug event bubbling in a multi-level interactive dropdown menu"
        ],
        "assessment": "20 JavaScript ES6+ MCQs + 1 algorithmic DOM asynchronous coding challenge.",
        "project_task": "Engineer an asynchronous real-time stocks and currency ticker widget using async/await and WebSocket streams."
    },
    "react": {
        "title": "Modern React & Component Architecture",
        "category": "Frontend Framework",
        "default_hours": 14,
        "difficulty": "Intermediate",
        "learning_objective": "Architect component-driven single page applications using functional React components, custom hooks, context state management, and optimized virtual DOM rendering.",
        "prerequisites": ["JavaScript"],
        "topics": [
            "Component Lifecycle & Virtual DOM: Declarative UI, JSX Compilation, and Reconciliation",
            "Core Hooks: useState, useEffect, useRef, useMemo, and useCallback for Performance Optimization",
            "Custom Hooks: Abstracting Reusable Business Logic and API Data Fetching",
            "State Architecture: Context API, useReducer Pattern, and Global State Management",
            "Component Routing with React Router, Lazy Loading, and Error Boundaries"
        ],
        "learning_resources": [
            {"title": "React Official Documentation (react.dev)", "type": "Documentation", "url": "https://react.dev/"},
            {"title": "Kent C. Dodds: Epic React Guides & Patterns", "type": "Guide", "url": "https://kentcdodds.com/blog"},
            {"title": "React Patterns and Best Practices by Alex Banks", "type": "Technical Resource", "url": "https://reactpatterns.com/"}
        ],
        "practice_activities": [
            "Build a custom useFetch hook featuring caching, auto-retry, and request cancellation",
            "Optimize a high-frequency rendering list using useMemo, useCallback, and React.memo",
            "Implement a multi-step user registration wizard with persistent Context state"
        ],
        "assessment": "20 React architecture MCQs + 1 interactive component coding assessment.",
        "project_task": "Construct a responsive Single Page Application with dynamic client-side filtering, modal dialogues, and global theme state management."
    },
    "java": {
        "title": "Enterprise Java & Object-Oriented System Architecture",
        "category": "Backend / Language",
        "default_hours": 14,
        "difficulty": "Advanced",
        "learning_objective": "Engineer robust backend enterprise services applying Java 17+, SOLID object-oriented principles, multithreading, concurrency utilities, and JVM memory management.",
        "prerequisites": [],
        "topics": [
            "Core OOP & SOLID Design Principles: Encapsulation, Polymorphism, Abstraction, and Liskov Substitution",
            "Java Collections Framework: Lists, Sets, HashMaps, B-Trees, and Custom Comparators",
            "Java Streams API, Functional Interfaces, Lambdas, and Optional Pipelines",
            "Multithreading & Concurrency: Executors, ThreadPools, Synchronized Blocks, and Concurrent Collections",
            "JVM Architecture: Heap/Stack Memory Allocation, Garbage Collection Algorithms (G1, ZGC), and Profiling"
        ],
        "learning_resources": [
            {"title": "Oracle Java SE 17 Documentation & Language Specification", "type": "Documentation", "url": "https://docs.oracle.com/en/java/javase/17/"},
            {"title": "Effective Java (3rd Edition) by Joshua Bloch", "type": "Book", "url": "https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/"},
            {"title": "Baeldung Java Tutorials and Guides", "type": "Technical Guide", "url": "https://www.baeldung.com/"}
        ],
        "practice_activities": [
            "Refactor a procedural data processor into clean SOLID polymorphic strategy patterns",
            "Process 200,000 transaction records in parallel using Java Streams and CompletableFuture",
            "Build a thread-safe multi-worker job execution queue using java.util.concurrent primitives"
        ],
        "assessment": "20 Core Java MCQs + 1 multithreaded coding challenge with strict unit test verification.",
        "project_task": "Develop an asynchronous multi-threaded order-processing engine handling concurrent queue submissions with thread-safe data persistence."
    },
    "sql": {
        "title": "Relational Database Design & SQL Querying",
        "category": "Database",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Model relational schemas to 3rd Normal Form, design primary/foreign key constraints, and write optimized multi-table queries with aggregate functions.",
        "prerequisites": [],
        "topics": [
            "Relational Database Modeling, Entity-Relationship (ER) Diagrams, and Normalization (1NF, 2NF, 3NF)",
            "DDL & DML: Tables, Constraints (NOT NULL, UNIQUE, CHECK, FK), and Cascade Deletions",
            "Multi-table JOIN Operations: INNER, LEFT, RIGHT, FULL OUTER, and Self-Joins",
            "Aggregate Functions, GROUP BY, HAVING Clauses, and Subquery Construction",
            "Database Indexing Fundamentals and Basic Query Execution Plans"
        ],
        "learning_resources": [
            {"title": "PostgreSQL Tutorial & Interactive Query Guide", "type": "Tutorial", "url": "https://www.postgresqltutorial.com/"},
            {"title": "Database System Concepts by Silberschatz, Korth, Sudarshan", "type": "Textbook", "url": "https://www.db-book.com/"},
            {"title": "W3Schools SQL Comprehensive Guide", "type": "Reference", "url": "https://www.w3schools.com/sql/"}
        ],
        "practice_activities": [
            "Normalize an unorganized flat sheet into a clean 3NF relational schema with strict constraints",
            "Author complex queries extracting customer purchasing frequencies and total expenditures using multi-joins",
            "Create database indices and analyze before/after query execution response times"
        ],
        "assessment": "15 Database design & SQL query MCQs + 1 practical schema design test.",
        "project_task": "Design and populate a normalized relational schema for a multi-tenant university course management system with integrity constraints."
    },
    "git": {
        "title": "Git Version Control & Collaborative DevOps Workflows",
        "category": "Version Control & DevOps",
        "default_hours": 6,
        "difficulty": "Intermediate",
        "learning_objective": "Command version control workflows, branch management, merge conflict resolution, rebasing, and collaborative pull-request reviews on GitHub/GitLab.",
        "prerequisites": [],
        "topics": [
            "Git Architecture: Working Directory, Staging Area, Local Repository, and Remote Tracking",
            "Branching Strategies: GitFlow, Trunk-Based Development, Feature Branches, and Tagging",
            "Merge Strategies: Fast-Forward, Three-Way Merges, Rebase vs Merge, and Conflict Resolution",
            "Advanced Git: Cherry-picking, Interactive Rebase, Stashing, Reflog, and Reset vs Revert",
            "Collaborative Engineering: Pull Requests, Code Review Standards, and Conventional Commits"
        ],
        "learning_resources": [
            {"title": "Pro Git Book by Scott Chacon and Ben Straub (Free)", "type": "Book", "url": "https://git-scm.com/book/en/v2"},
            {"title": "GitHub Git and Version Control Documentation", "type": "Documentation", "url": "https://docs.github.com/en/get-started"},
            {"title": "Atlassian Git Tutorial and Workflows", "type": "Guide", "url": "https://www.atlassian.com/git/tutorials"}
        ],
        "practice_activities": [
            "Simulate and resolve complex merge conflicts across two divergent feature branches",
            "Use interactive rebase to squash multiple WIP commit logs into clean semantic milestones",
            "Recover an accidentally deleted commit using the git reflog audit history"
        ],
        "assessment": "15 Git commands and branching scenarios MCQs + 1 merge conflict resolution exercise.",
        "project_task": "Initialize, structure, and configure a multi-branch team repository implementing strict PR protection rules and semantic versioning tags."
    },
    "rest api": {
        "title": "RESTful API Architecture & Secure Service Design",
        "category": "Web Architecture",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Design and build RESTful web services adhering to HTTP semantics, status codes, stateless authentication (JWT), pagination, and API documentation standards.",
        "prerequisites": ["JavaScript", "Java"],
        "topics": [
            "REST Architectural Constraints: Statelessness, Client-Server, Cacheability, and Layered Systems",
            "HTTP Protocol Semantics: Idempotent Methods (GET, PUT, DELETE), Safe Methods, and Status Codes",
            "Resource Modeling: URI Naming Conventions, Query Parameters, Filtering, Sorting, and Pagination",
            "API Security: JWT Bearer Tokens, CORS Policies, Rate Limiting, and Input Validation",
            "OpenAPI / Swagger Documentation, Postman Collections, and Automated Contract Testing"
        ],
        "learning_resources": [
            {"title": "RESTful Web APIs by Leonard Richardson and Mike Amundsen", "type": "Book", "url": "https://www.oreilly.com/library/view/restful-web-apis/9781449359713/"},
            {"title": "Microsoft REST API Guidelines", "type": "Specification", "url": "https://github.com/microsoft/api-guidelines"},
            {"title": "Swagger / OpenAPI Specification Guide", "type": "Documentation", "url": "https://swagger.io/specification/"}
        ],
        "practice_activities": [
            "Design an OpenAPI 3.0 specification for an e-commerce catalog API with pagination and filtering",
            "Implement JWT token validation and role-based route middleware in an HTTP backend",
            "Write automated contract integration tests checking HTTP status code compliance"
        ],
        "assessment": "15 REST API architecture MCQs + 1 endpoint design challenge.",
        "project_task": "Build a secure RESTful service featuring CRUD operations, JWT authentication, query-string pagination, and interactive Swagger documentation."
    },
    "html/css": {
        "title": "Semantic HTML5, Modern CSS & Responsive Layouts",
        "category": "Web Standards",
        "default_hours": 6,
        "difficulty": "Intermediate",
        "learning_objective": "Construct accessible, standards-compliant web pages using semantic HTML5 elements, CSS Flexbox, CSS Grid, custom properties, and responsive media queries.",
        "prerequisites": [],
        "topics": [
            "Semantic HTML5 Elements: Header, Nav, Main, Article, Section, Aside, and Footer",
            "CSS Box Model: Margins, Borders, Padding, Content, and box-sizing: border-box",
            "Modern Layout Systems: CSS Flexbox (1D) and CSS Grid (2D) for Complex Responsive Grids",
            "Responsive Web Design: Mobile-First Approach, Fluid Typography, and Media Queries",
            "Web Accessibility (a11y): ARIA Attributes, Color Contrast, and Screen Reader Standards"
        ],
        "learning_resources": [
            {"title": "MDN Web Docs: Learn HTML & CSS", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML"},
            {"title": "CSS-Tricks: A Complete Guide to Flexbox & CSS Grid", "type": "Guide", "url": "https://css-tricks.com/"},
            {"title": "WebAIM: Web Accessibility Guidelines", "type": "Guidelines", "url": "https://webaim.org/"}
        ],
        "practice_activities": [
            "Construct a fully responsive 3-column dashboard layout that stacks cleanly on mobile viewports",
            "Build an accessible navigation bar with ARIA attributes and keyboard focus management",
            "Implement a dark/light theme toggle using CSS Custom Properties (CSS variables)"
        ],
        "assessment": "15 HTML5 & CSS responsive design MCQs + 1 responsive layout challenge.",
        "project_task": "Develop a multi-device responsive product landing page adhering strictly to W3C semantic markup and WCAG AA accessibility contrast ratios."
    },
    "python": {
        "title": "Python Core & Advanced System Automation",
        "category": "Backend / Scripting",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Master core and advanced Python programming, object-oriented design, exception handling, data structures, and algorithmic efficiency.",
        "prerequisites": [],
        "topics": [
            "Python Data Model: Dictionaries, Sets, Lists, Tuples, and Memory References",
            "Object-Oriented Python: Dunder Methods, Inheritance, Properties, and Abstract Classes",
            "Functional Tools: Itertools, Functools (lru_cache), Map, Filter, and Generator Functions",
            "Exception Hierarchies, Context Managers (with statement), and Custom Contexts",
            "Testing & Quality: Unit Testing with Pytest, Type Hints (typing module), and Linting"
        ],
        "learning_resources": [
            {"title": "Fluent Python (2nd Edition) by Luciano Ramalho", "type": "Book", "url": "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/"},
            {"title": "Official Python 3 Documentation", "type": "Documentation", "url": "https://docs.python.org/3/"},
            {"title": "Real Python Tutorials & Engineering Guides", "type": "Tutorials", "url": "https://realpython.com/"}
        ],
        "practice_activities": [
            "Implement a custom generator-based streaming parser reading large log files line-by-line",
            "Build a custom caching decorator utilizing functools.wraps and dynamic arguments",
            "Write comprehensive pytest test suites covering edge cases and exception branches"
        ],
        "assessment": "20 Python Core MCQs + 1 algorithmic challenge with test cases.",
        "project_task": "Engineer an automated server monitoring script with custom context managers and structured JSON logging."
    },
    "python basics": {
        "title": "Python Basics & Core Language Syntax",
        "category": "Programming Fundamentals",
        "default_hours": 8,
        "difficulty": "Beginner",
        "learning_objective": "Master Python syntax, primitive types, operators, branching conditionals, and loops to build procedural programs.",
        "prerequisites": [],
        "topics": [
            "Python Execution Model, Virtual Environments, and REPL",
            "Variables, Primitive Types (int, float, str, bool), and Type Casting",
            "Arithmetic, Comparison, and Logical Operators",
            "Conditional Control Flow: if, elif, and else Statements",
            "Iteration: while Loops, for Loops, and range() Generators"
        ],
        "learning_resources": [
            {"title": "Official Python Tutorial: Whetting Your Appetite", "type": "Documentation", "url": "https://docs.python.org/3/tutorial/"},
            {"title": "Automate the Boring Stuff with Python", "type": "Book", "url": "https://automatetheboringstuff.com/"},
            {"title": "CS50's Introduction to Programming with Python", "type": "Course", "url": "https://cs50.harvard.edu/python/"}
        ],
        "practice_activities": [
            "Implement a console currency converter with robust type checking and input loops",
            "Write a loop-based prime number generator calculating primes up to 10,000",
            "Build a command-line calculator supporting chained arithmetic operations"
        ],
        "assessment": "15 MCQs covering Python operators, type conversions, and loop mechanics + 1 console coding challenge.",
        "project_task": "Develop an interactive text-based banking ledger application handling deposits, withdrawals, and balance verification."
    },
    "python functions": {
        "title": "Python Functions, Modularization & Scope",
        "category": "Modular Programming",
        "default_hours": 8,
        "difficulty": "Beginner",
        "learning_objective": "Architect maintainable Python code utilizing modular functions, parameter passing, LEGB scope hierarchies, and first-class functions.",
        "prerequisites": ["Python Basics"],
        "topics": [
            "Function Signatures, Default Arguments, and Keyword Arguments",
            "Variable Length Arguments: *args and **kwargs Unpacking",
            "Variable Scope Rules: Local, Enclosing, Global, and Built-in (LEGB)",
            "First-Class Functions, Closures, and Higher-Order Functions",
            "Type Annotations (PEP 484), Docstrings, and Unit Testing Fundamentals"
        ],
        "learning_resources": [
            {"title": "Python Documentation: Defining Functions", "type": "Documentation", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions"},
            {"title": "Real Python: Defining Your Own Python Function", "type": "Guide", "url": "https://realpython.com/defining-your-own-python-function/"},
            {"title": "Google Python Style Guide", "type": "Style Guide", "url": "https://google.github.io/styleguide/pyguide.html"}
        ],
        "practice_activities": [
            "Refactor a 200-line monolithic script into single-responsibility pure functions",
            "Build a math calculation module using *args and **kwargs to compute arbitrary summary statistics",
            "Implement a retry decorator using function closures to handle transient operations"
        ],
        "assessment": "15 Function scope, recursion, and signature MCQs + 1 modular refactoring challenge.",
        "project_task": "Engineer a modular mathematical transformation and string parsing utility library with comprehensive docstrings and unit tests."
    },
    "python data structures": {
        "title": "Python Data Structures & Collections Engineering",
        "category": "Data Structures & Collections",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Master Python's built-in collection structures, algorithmic time complexities, list/dict comprehensions, and the collections module for efficient in-memory data processing.",
        "prerequisites": ["Python Functions"],
        "topics": [
            "Sequence Types: Lists, Tuples, Slicing Semantics, and Memory References",
            "Hash-Based Collections: Dictionaries, Sets, Hash Collisions, and Key Invariants",
            "Comprehensions: List, Set, and Dictionary Comprehensions with Nested Filters",
            "Advanced Collections Module: deque, Counter, defaultdict, and namedtuple",
            "Algorithmic Complexity (Big-O) of Common Collection Operations"
        ],
        "learning_resources": [
            {"title": "Python Data Structures Documentation", "type": "Documentation", "url": "https://docs.python.org/3/tutorial/datastructures.html"},
            {"title": "Problem Solving with Algorithms and Data Structures in Python", "type": "Textbook", "url": "https://runestone.academy/ns/books/published/pythonds/index.html"},
            {"title": "Real Python: Python's collections Module", "type": "Guide", "url": "https://realpython.com/python-collections-module/"}
        ],
        "practice_activities": [
            "Implement an LRU cache or ring buffer using collections.deque with O(1) inserts",
            "Transform nested unstructured JSON payloads into clean flat dictionary lookups using comprehensions",
            "Analyze time complexities of list membership lookups vs set lookups over 1,000,000 elements"
        ],
        "assessment": "15 Data structure mechanics & Big-O MCQs + 1 collections algorithmic problem.",
        "project_task": "Develop an in-memory high-throughput transaction indexing engine that organizes purchase records by category, date, and user ID with sub-millisecond retrieval."
    },
    "data analysis": {
        "title": "Applied Data Analysis & Exploratory Insights",
        "category": "Analytics & Insights",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Execute end-to-end data analysis workflows from data cleaning to hypothesis testing and business insight extraction using Pandas, NumPy, and statistical methods.",
        "prerequisites": ["Pandas"],
        "topics": [
            "Exploratory Data Analysis (EDA) Workflows and Hypothesis Formulation",
            "Data Cleaning: Missing Value Imputation, Outlier Detection (IQR / Z-score), and Encoding",
            "Multivariate Aggregations, Group-by Operations, and Cohort Segmentation",
            "Correlation Metrics, Statistical Significance, and Trend Detection",
            "Translating Analytical Findings into Actionable Executive Recommendations"
        ],
        "learning_resources": [
            {"title": "Python Data Science Handbook by Jake VanderPlas", "type": "Book", "url": "https://jakevdp.github.io/PythonDataScienceHandbook/"},
            {"title": "Pandas User Guide & Cookbook", "type": "Documentation", "url": "https://pandas.pydata.org/docs/user_guide/index.html"},
            {"title": "Kaggle: Exploratory Data Analysis Best Practices", "type": "Tutorial", "url": "https://www.kaggle.com/learn/data-cleaning"}
        ],
        "practice_activities": [
            "Perform end-to-end exploratory data analysis on a 100,000-row customer churn dataset",
            "Segment marketing campaigns using cross-tabulation and statistical uplift metrics",
            "Identify and impute missing behavioral data using distribution-preserving strategies"
        ],
        "assessment": "15 Data analysis case study MCQs + 1 practical EDA dataset investigation challenge.",
        "project_task": "Conduct a comprehensive data analysis study on product churn telemetry, presenting validated statistical insights and strategic growth recommendations."
    },
    "algorithms": {
        "title": "Algorithms & Algorithmic Complexity Engineering",
        "category": "Computer Science Core",
        "default_hours": 14,
        "difficulty": "Intermediate",
        "learning_objective": "Analyze asymptotic time/space complexity, implement recursion, divide-and-conquer, sorting/searching, and dynamic programming algorithms.",
        "prerequisites": [],
        "topics": [
            "Asymptotic Complexity: Big-O, Big-Omega, Big-Theta, and Auxiliary Space",
            "Divide-and-Conquer: Binary Search, Merge Sort, and Quick Sort",
            "Graph Traversal & Search: Breadth-First Search (BFS) and Depth-First Search (DFS)",
            "Greedy Algorithms and Dynamic Programming Fundamentals (Memoization / Tabulation)",
            "Trees & Binary Search Trees: Inorder, Preorder, Postorder, and Tree Balancing Concepts"
        ],
        "learning_resources": [
            {"title": "Introduction to Algorithms (CLRS 4th Edition)", "type": "Textbook", "url": "https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/"},
            {"title": "Grokking Algorithms by Aditya Bhargava", "type": "Book", "url": "https://www.manning.com/books/grokking-algorithms"},
            {"title": "VisuAlgo: Visualising Data Structures and Algorithms", "type": "Interactive", "url": "https://visualgo.net/"}
        ],
        "practice_activities": [
            "Implement Binary Search with boundary condition verification across duplicate keys",
            "Write BFS and DFS graph traversals computing shortest paths in unweighted networks",
            "Solve the 0/1 Knapsack problem using dynamic programming with memoization"
        ],
        "assessment": "20 Algorithm design MCQs + 2 algorithmic coding problems with strict execution benchmarks.",
        "project_task": "Engineer an optimized route-planning engine applying graph search algorithms to compute shortest paths between interconnected distribution hubs."
    },
    "problem solving": {
        "title": "Technical Problem Solving & Interview Patterns",
        "category": "Core CS",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Deconstruct complex algorithmic problems into optimal data structures, two-pointer techniques, sliding windows, and backtracking solutions.",
        "prerequisites": ["Algorithms"],
        "topics": [
            "Two-Pointer Techniques and Sliding Window String/Array Optimizations",
            "Monotonic Stacks and Priority Queues (Heaps) for Top-K Streaming Problems",
            "Backtracking Strategies: Permutations, Combinations, and Constraint Satisfaction",
            "Trie Data Structures for Prefix Matching and High-Speed Autocomplete",
            "Systematic Edge Case Analysis and Time-Constrained Debugging Patterns"
        ],
        "learning_resources": [
            {"title": "Cracking the Coding Interview by Gayle Laakmann McDowell", "type": "Book", "url": "https://www.crackingthecodinginterview.com/"},
            {"title": "NeetCode: Algorithms Roadmap & Patterns", "type": "Guide", "url": "https://neetcode.io/"},
            {"title": "LeetCode Curated Problem Patterns", "type": "Interactive", "url": "https://leetcode.com/"}
        ],
        "practice_activities": [
            "Solve longest substring without repeating characters using sliding window in O(N) time",
            "Implement a top-K frequent elements tracker using a min-heap in O(N log K) time",
            "Generate all valid Sudoku board configurations using recursive backtracking"
        ],
        "assessment": "15 Problem decomposition MCQs + 2 live timed programming challenges.",
        "project_task": "Engineer a high-performance in-memory search prefix suggestion engine utilizing a Trie data structure with O(L) autocomplete lookup."
    },
    "cloud": {
        "title": "Cloud Computing Architecture & Distributed Systems",
        "category": "Cloud & Infrastructure",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Design resilient cloud architectures using virtualized compute, object storage, serverless functions, VPC networking, and IAM security policies.",
        "prerequisites": [],
        "topics": [
            "Cloud Fundamentals: IaaS vs PaaS vs SaaS, Multi-Region Availability, and SLAs",
            "Compute & Virtualization: Virtual Machines, Auto-Scaling Groups, and Serverless Compute",
            "Cloud Storage Systems: Block Storage, File Systems, and Object Storage (S3 / Blob)",
            "Virtual Private Cloud (VPC): Subnets, Route Tables, NAT Gateways, and Security Groups",
            "Identity & Access Management (IAM): Least-Privilege Policies, Roles, and Key Rotation"
        ],
        "learning_resources": [
            {"title": "AWS Cloud Practitioner & Architect Whitepapers", "type": "Documentation", "url": "https://aws.amazon.com/whitepapers/"},
            {"title": "Google Cloud Architecture Framework", "type": "Guide", "url": "https://cloud.google.com/architecture/framework"},
            {"title": "Microsoft Learn: Azure Fundamentals", "type": "Course", "url": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/"}
        ],
        "practice_activities": [
            "Configure a secure multi-tier VPC network with public web subnets and isolated database subnets",
            "Deploy an automated serverless function triggered by object storage upload events",
            "Draft an IAM policy granting read-only access to specific S3 buckets based on tags"
        ],
        "assessment": "20 Cloud architecture & security MCQs + 1 cloud deployment scenario evaluation.",
        "project_task": "Architect and document a high-availability multi-tier cloud infrastructure diagram with auto-scaling, load balancing, and failover disaster recovery."
    },
    "devops": {
        "title": "DevOps Engineering, CI/CD & Automated Delivery",
        "category": "DevOps & Automation",
        "default_hours": 14,
        "difficulty": "Advanced",
        "learning_objective": "Construct automated continuous integration and continuous deployment (CI/CD) pipelines, containerize microservices with Docker, and automate infrastructure.",
        "prerequisites": ["Git"],
        "topics": [
            "DevOps Cultural Principles: Continuous Delivery, Observability, and Fast Feedback Loops",
            "Containerization with Docker: Dockerfile Directives, Multi-Stage Builds, and Image Optimization",
            "Automated CI/CD Pipelines: GitHub Actions, Runners, Secrets, and Artifact Publishing",
            "Infrastructure as Code (IaC) Foundations: Declarative vs Imperative Configuration",
            "System Observability: Centralized Logging, Prometheus Metrics, and Health Check Probes"
        ],
        "learning_resources": [
            {"title": "Docker Official Documentation & Guides", "type": "Documentation", "url": "https://docs.docker.com/"},
            {"title": "GitHub Actions Documentation", "type": "Documentation", "url": "https://docs.github.com/en/actions"},
            {"title": "The Phoenix Project: A Novel about IT and DevOps", "type": "Book", "url": "https://itrevolution.com/product/the-phoenix-project/"}
        ],
        "practice_activities": [
            "Containerize a Python/FastAPI web application using a multi-stage Docker build under 100MB",
            "Author a GitHub Actions workflow that executes linters, unit tests, and builds Docker images on PRs",
            "Configure Docker Compose orchestrating an API server, Redis cache, and PostgreSQL database"
        ],
        "assessment": "20 DevOps and containerization MCQs + 1 CI/CD pipeline authoring challenge.",
        "project_task": "Build and deploy a fully automated CI/CD pipeline that tests, packages, and deploys a multi-container web application to a staging environment."
    },
    "docker": {
        "title": "Docker Containerization & Microservice Packaging",
        "category": "DevOps & Infrastructure",
        "default_hours": 10,
        "difficulty": "Intermediate",
        "learning_objective": "Build, run, and optimize containerized environments using Docker, multi-stage Dockerfiles, Docker Compose, and container registry management.",
        "prerequisites": ["Git"],
        "topics": [
            "Containerization Fundamentals: Virtual Machines vs Containers, Namespaces, and Cgroups",
            "Dockerfile Directives: FROM, WORKDIR, COPY, RUN, CMD, and Multi-Stage Optimization",
            "Docker Networking: Bridge, Host, Overlay, and Port Forwarding",
            "Persistent Storage: Volumes, Bind Mounts, and Data Safety",
            "Multi-Container Orchestration: Docker Compose, Healthchecks, and Environment Variables"
        ],
        "learning_resources": [
            {"title": "Docker Official Get Started Documentation", "type": "Documentation", "url": "https://docs.docker.com/get-started/"},
            {"title": "Docker Deep Dive by Nigel Poulton", "type": "Book", "url": "https://nigelpoulton.com/docker-deep-dive/"},
            {"title": "Play with Docker Interactive Labs", "type": "Interactive", "url": "https://labs.play-with-docker.com/"}
        ],
        "practice_activities": [
            "Write a multi-stage Dockerfile packaging a Python FastAPI backend into a distroless runtime",
            "Author a docker-compose.yml file standing up an application service, PostgreSQL database, and Redis cache",
            "Inspect container memory usage and configure cgroup resource limits"
        ],
        "assessment": "15 Containerization & Dockerfile optimization MCQs + 1 multi-container composition challenge.",
        "project_task": "Containerize an end-to-end full-stack web application with automated multi-container Docker Compose orchestration and database volume persistence."
    },
    "system design": {
        "title": "Distributed Systems Architecture & Scalability",
        "category": "Architecture & Systems",
        "default_hours": 14,
        "difficulty": "Advanced",
        "learning_objective": "Architect distributed systems handling millions of concurrent users applying load balancing, caching tiers, database sharding, message queues, and CAP theorem trade-offs.",
        "prerequisites": ["REST API", "SQL"],
        "topics": [
            "Horizontal vs Vertical Scaling, Load Balancers (L4/L7), and Reverse Proxies",
            "Caching Strategies: Redis/Memcached, Cache-Aside, Write-Through, and Eviction Policies (LRU)",
            "Database Scaling: Read Replicas, Horizontal Sharding, Consistent Hashing, and NoSQL vs SQL",
            "Asynchronous Decoupling: Message Queues (Kafka, RabbitMQ), Event-Driven Architecture",
            "CAP Theorem, Eventual Consistency, Distributed Transactions, and Rate Limiting"
        ],
        "learning_resources": [
            {"title": "Designing Data-Intensive Applications by Martin Kleppmann", "type": "Book", "url": "https://dataintensive.net/"},
            {"title": "System Design Primer by Donne Martin", "type": "Guide", "url": "https://github.com/donnemartin/system-design-primer"},
            {"title": "High Scalability Real-World Architecture Case Studies", "type": "Reference", "url": "http://highscalability.com/"}
        ],
        "practice_activities": [
            "Design an end-to-end URL shortening service (like TinyURL) capable of 10,000 writes/sec",
            "Calculate storage, bandwidth, and memory capacity requirements for a photo-sharing platform",
            "Map out consistent hashing ring behavior upon node addition and node failure"
        ],
        "assessment": "20 Distributed system design scenario MCQs + 1 architectural design proposal.",
        "project_task": "Author an architectural design specification document for a real-time collaborative notification platform with caching, message brokers, and horizontal scale."
    },
    "web development": {
        "title": "Full-Stack Web Development & Modern Integration",
        "category": "Web Engineering",
        "default_hours": 12,
        "difficulty": "Intermediate",
        "learning_objective": "Integrate client-side user interfaces with server-side application logic, database persistence, and secure authentication flows.",
        "prerequisites": ["HTML/CSS", "JavaScript"],
        "topics": [
            "Client-Server Architecture: HTTP Request/Response Cycles, Headers, and Cookies",
            "RESTful API Integration with Modern Frontend Frameworks",
            "State Synchronization, Asynchronous Data Fetching, and Optimistic UI Updates",
            "User Authentication: Session Cookies vs JSON Web Tokens (JWT) and Security Best Practices",
            "Web Security Fundamentals: Cross-Site Scripting (XSS), CSRF, and Content Security Policy (CSP)"
        ],
        "learning_resources": [
            {"title": "MDN Web Docs: Web Development Guides", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Learn"},
            {"title": "OWASP Top Ten Web Application Security Risks", "type": "Security Guide", "url": "https://owasp.org/www-project-top-ten/"},
            {"title": "Full Stack Open by University of Helsinki", "type": "Course", "url": "https://fullstackopen.com/en/"}
        ],
        "practice_activities": [
            "Build a full-stack CRUD application connecting a client UI to a REST API backend",
            "Implement secure token storage and route guarding in a single page application",
            "Sanitize user inputs to prevent XSS injection attacks"
        ],
        "assessment": "15 Web architecture & security MCQs + 1 integration coding assessment.",
        "project_task": "Develop an end-to-end full-stack web application featuring user authentication, database persistence, and a responsive frontend interface."
    }
}

def get_capstone_module_definition(target_role_title: str) -> Dict[str, Any]:
    """Generates the capstone integration project module."""
    return {
        "skill_name": "Capstone Project",
        "title": f"Production Engineering Capstone: {target_role_title}",
        "category": "Capstone Integration",
        "current_proficiency": "Ready to Synthesize",
        "required_proficiency": "Expert / Production",
        "difficulty": "Advanced",
        "hours": 16,
        "learning_objective": f"Synthesize all mastered competencies into an end-to-end, production-grade deliverable demonstrating verified job readiness for {target_role_title}.",
        "prerequisites": ["All Curriculum Modules"],
        "topics": [
            "System Architecture & End-to-End Design Specification",
            "Implementation of Core Competencies & Best Practices",
            "Automated Testing, Verification & Integration Checks",
            "Documentation, Deployment Runbook & Portfolio Presentation"
        ],
        "learning_resources": [
            {"title": "Software Engineering Best Practices & Architecture", "type": "Guide", "url": "https://12factor.net/"},
            {"title": "Engineering Project Portfolio Documentation Standards", "type": "Reference", "url": "https://github.com"}
        ],
        "practice_activities": [
            "Draft architectural specification and data flow diagram",
            "Conduct end-to-end integration and load testing",
            "Prepare clean GitHub repository with README runbook and recorded demo"
        ],
        "assessment": "Final holistic peer and automated review evaluating code quality, test coverage, and documentation.",
        "project_task": f"Deliver and present an end-to-end {target_role_title} application featuring complete technical implementation, tests, and clean architecture."
    }

def topological_sort_modules(modules_list: List[Dict[str, Any]], learning_preferences: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Strict Prerequisite Ordering Logic:
    Performs topological ordering over modules based on their prerequisite dependencies.
    Ensures foundational modules (e.g. Python Basics -> Python Functions -> Python Data Structures -> Pandas -> Data Analysis)
    always precede dependent modules.
    Within independent tiers, prioritizes by:
    1. Skill gap magnitude (descending)
    2. Job-market demand % (descending)
    3. Role importance weight (descending)
    4. User learning preferences match (descending)
    """
    skill_to_module = {m["skill_name"].lower(): m for m in modules_list}

    # Build dependency graph
    in_degree = {m["skill_name"].lower(): 0 for m in modules_list}
    dependents_graph = {m["skill_name"].lower(): [] for m in modules_list}

    for m in modules_list:
        s_lower = m["skill_name"].lower()
        prereqs = m.get("prerequisites", [])
        for pr in prereqs:
            pr_lower = pr.lower()
            if pr_lower in skill_to_module:
                in_degree[s_lower] += 1
                dependents_graph[pr_lower].append(s_lower)

    # Queue of nodes with 0 incoming dependencies
    queue = [s for s, deg in in_degree.items() if deg == 0]

    # Sort queue by priority: gap_num desc, demand desc, importance desc, preference match desc
    def priority_sort_key(s_name: str):
        mod = skill_to_module[s_name]
        pref_match = 0
        if learning_preferences:
            lp_lower = learning_preferences.lower()
            terms = [t.strip() for t in lp_lower.replace('&', ' ').replace('/', ' ').split() if len(t.strip()) > 2]
            target_text = f"{mod.get('skill_name', '')} {mod.get('category', '')} {' '.join(mod.get('topics', []))}".lower()
            if any(term in target_text for term in terms):
                pref_match = 1
        return (
            -mod.get("gap_num", 0),
            -mod.get("job_demand_percentage", 0),
            -mod.get("importance_weight", 0),
            -pref_match
        )

    queue.sort(key=priority_sort_key)

    sorted_skills = []
    while queue:
        current = queue.pop(0)
        sorted_skills.append(current)

        for dep in dependents_graph[current]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)
                queue.sort(key=priority_sort_key)

    # If any cycle or unreached nodes, append them
    for m in modules_list:
        s_lower = m["skill_name"].lower()
        if s_lower not in sorted_skills:
            sorted_skills.append(s_lower)

    return [skill_to_module[s] for s in sorted_skills]

def generate_personalized_curriculum(
    user_id: int,
    target_role_id: Optional[str] = None,
    weekly_hours: int = 10,
    preferred_difficulty: str = "Adaptive",
    learning_preferences: str = "Hands-on Projects & Coding"
) -> Dict[str, Any]:
    """
    Module 6 Core:
    Synthesizes a personalized, non-generic AI Curriculum directly from:
    1. Verified user skill profile (Module 3)
    2. Identified skill gaps (Module 5)
    3. Target job role (Module 1)
    4. Job-market demand (Module 4)
    5. Skill priority tiers (Module 5)
    6. Strict prerequisite dependencies (foundational -> advanced)
    7. User learning preferences & weekly pacing
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Resolve Target Role
    if not target_role_id:
        cursor.execute("SELECT target_role_id FROM career_profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        target_role_id = p_row["target_role_id"] if p_row and p_row["target_role_id"] else "fullstack-dev"

    cursor.execute("SELECT * FROM job_roles WHERE LOWER(role_id) = LOWER(?)", (target_role_id,))
    role_info = cursor.fetchone()
    if not role_info:
        cursor.execute("SELECT * FROM job_roles WHERE role_id = 'fullstack-dev'")
        role_info = cursor.fetchone()
        target_role_id = "fullstack-dev"

    role_id = role_info["role_id"]
    role_title = role_info["role_title"]

    # 2. Compute live skill gaps for this user and role (Module 5)
    gap_data = calculate_skill_gaps(user_id=user_id, target_role_id=role_id)
    gaps = gap_data.get("gaps", [])

    # If all skills have 0 gap (already mastered), still include skills to keep them refreshed or advance
    actionable_gaps = [g for g in gaps if g["gap_num"] > 0]
    if not actionable_gaps:
        actionable_gaps = gaps[:6]

    # 3. Formulate structured 12-field modules for each skill gap
    raw_modules = []
    for g in actionable_gaps:
        s_name = g["skill_name"]
        s_lower = s_name.lower()

        # Look up rich knowledge template
        template = MODULE_KNOWLEDGE_BASE.get(s_lower)
        if not template:
            # Fallback template with rich defaults
            template = {
                "title": f"{s_name} Engineering Mastery",
                "category": g.get("category", "Core Technical"),
                "default_hours": 10,
                "difficulty": "Intermediate" if g["required_level_num"] <= 3 else "Advanced",
                "learning_objective": f"Develop production-level proficiency in {s_name} to bridge verified competency requirements.",
                "prerequisites": [],
                "topics": [
                    f"Core Concepts and Syntactical Foundations of {s_name}",
                    f"Architectural Patterns & Best Practices in {s_name}",
                    f"Testing, Debugging and Exception Handling for {s_name}",
                    f"Performance Tuning and Scalability Strategies in {s_name}"
                ],
                "learning_resources": [
                    {"title": f"Official {s_name} Documentation & Reference", "type": "Documentation", "url": "https://devdocs.io"},
                    {"title": f"Practical Guide to {s_name}", "type": "Guide", "url": "https://github.com"}
                ],
                "practice_activities": [
                    f"Complete 3 hands-on programming drills in {s_name}",
                    f"Build a modular component applying {s_name} principles"
                ],
                "assessment": f"15 {s_name} MCQs + 1 practical coding challenge.",
                "project_task": f"Build and document a functional {s_name} module adhering to production quality standards."
            }

        # Calculate estimated duration: adjusted by gap magnitude (e.g. 1 gap level = 6 hrs, 2 = 10 hrs, 3 = 14 hrs)
        gap_hours = max(6, g["gap_num"] * 4 + 2) if g["gap_num"] > 0 else template.get("default_hours", 8)

        # Calibrate difficulty based on required proficiency
        calibrated_difficulty = g["required_level"] if g["required_level"] in ["Beginner", "Intermediate", "Advanced"] else template.get("difficulty", "Intermediate")

        mod_dict = {
            "skill_name": s_name,
            "title": template["title"],
            "category": template.get("category", g.get("category", "Technical")),
            "current_proficiency": g["verified_level"],
            "current_proficiency_num": g["verified_level_num"],
            "required_proficiency": g["required_level"],
            "required_proficiency_num": g["required_level_num"],
            "gap": g["gap"],
            "gap_num": g["gap_num"],
            "job_demand_percentage": g.get("job_demand_percentage", 75.0),
            "importance_weight": g.get("importance_weight", 0.85),
            "priority": g["priority"],
            "priority_badge_class": g.get("priority_badge_class", "badge-primary"),
            "learning_objective": template["learning_objective"],
            "prerequisites": template["prerequisites"],
            "topics": template["topics"],
            "difficulty": calibrated_difficulty,
            "hours": gap_hours,
            "estimated_duration": f"{gap_hours} Hours",
            "learning_resources": template["learning_resources"],
            "practice_activities": template["practice_activities"],
            "assessment": template["assessment"],
            "project_task": template["project_task"],
            "status": "pending",
            "progress_pct": 0,
            "is_unlocked": True
        }
        raw_modules.append(mod_dict)

    # 4. Strict Prerequisite Topological Sorting & Multi-Factor Priority Sequencing
    sequenced_modules = topological_sort_modules(raw_modules, learning_preferences=learning_preferences)

    # 5. Append Final Capstone Integration Project
    capstone_def = get_capstone_module_definition(role_title)
    sequenced_modules.append({
        "skill_name": capstone_def["skill_name"],
        "title": capstone_def["title"],
        "category": capstone_def["category"],
        "current_proficiency": capstone_def["current_proficiency"],
        "current_proficiency_num": 0,
        "required_proficiency": capstone_def["required_proficiency"],
        "required_proficiency_num": 5,
        "gap": "Integration Capstone",
        "gap_num": 1,
        "job_demand_percentage": 100.0,
        "importance_weight": 1.0,
        "priority": "Critical",
        "priority_badge_class": "badge-danger",
        "learning_objective": capstone_def["learning_objective"],
        "prerequisites": [m["skill_name"] for m in sequenced_modules],
        "topics": capstone_def["topics"],
        "difficulty": capstone_def["difficulty"],
        "hours": capstone_def["hours"],
        "estimated_duration": f"{capstone_def['hours']} Hours",
        "learning_resources": capstone_def["learning_resources"],
        "practice_activities": capstone_def["practice_activities"],
        "assessment": capstone_def["assessment"],
        "project_task": capstone_def["project_task"],
        "status": "pending",
        "progress_pct": 0,
        "is_unlocked": False
    })

    # Set unlocking: first module is unlocked; subsequent modules locked if prerequisites not done
    completed_skills = set()
    for idx, m in enumerate(sequenced_modules):
        m["module_order"] = idx + 1
        # Check prerequisites
        prereqs = m.get("prerequisites", [])
        if not prereqs or all(p.lower() in completed_skills for p in prereqs):
            m["is_unlocked"] = True
        else:
            m["is_unlocked"] = (idx == 0)

    # 6. Timeline and Pacing Calculation
    total_hours = sum(m["hours"] for m in sequenced_modules)
    active_weekly_hours = max(5, int(weekly_hours or 10))
    estimated_weeks = max(1, math.ceil(total_hours / active_weekly_hours))

    # 7. Persist to Database: user_curriculums and curriculum_modules
    cursor.execute("""
    SELECT id, adaptation_version FROM user_curriculums
    WHERE user_id = ? AND LOWER(role_id) = LOWER(?)
    """, (user_id, role_id))
    existing_curr = cursor.fetchone()

    curriculum_title = f"Personalized Micro-Credential Pathway: {role_title}"

    if existing_curr:
        curr_id = existing_curr["id"]
        version = existing_curr["adaptation_version"] + 1
        cursor.execute("""
        UPDATE user_curriculums
        SET title = ?, status = 'active', total_modules = ?, adaptation_version = ?,
            weekly_hours = ?, preferred_difficulty = ?, learning_preferences = ?,
            estimated_weeks = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (
            curriculum_title, len(sequenced_modules), version,
            active_weekly_hours, preferred_difficulty, learning_preferences,
            estimated_weeks, curr_id
        ))
        # Clear previous module records for clean synthesis
        cursor.execute("DELETE FROM curriculum_modules WHERE curriculum_id = ?", (curr_id,))
    else:
        version = 1
        cursor.execute("""
        INSERT INTO user_curriculums (
            user_id, role_id, title, status, total_modules, completed_modules,
            adaptation_version, weekly_hours, preferred_difficulty,
            learning_preferences, estimated_weeks
        ) VALUES (?, ?, ?, 'active', ?, 0, ?, ?, ?, ?, ?)
        """, (
            user_id, role_id, curriculum_title, len(sequenced_modules),
            version, active_weekly_hours, preferred_difficulty,
            learning_preferences, estimated_weeks
        ))
        curr_id = cursor.lastrowid

    # Persist individual modules
    for m in sequenced_modules:
        cursor.execute("""
        INSERT INTO curriculum_modules (
            curriculum_id, module_order, title, hours, status, progress_pct,
            skill_name, current_proficiency, required_proficiency, difficulty,
            learning_objective, prerequisites_json, topics_json, resources_json,
            practice_json, assessment_info, project_task, details_json, is_unlocked
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            curr_id, m["module_order"], m["title"], m["hours"], m["status"], m["progress_pct"],
            m["skill_name"], m["current_proficiency"], m["required_proficiency"], m["difficulty"],
            m["learning_objective"], json.dumps(m["prerequisites"]), json.dumps(m["topics"]),
            json.dumps(m["learning_resources"]), json.dumps(m["practice_activities"]),
            m["assessment"], m["project_task"], json.dumps(m), 1 if m["is_unlocked"] else 0
        ))
        m["module_id"] = cursor.lastrowid

    # Format micro-credentials for backwards compatibility and badge rendering
    cursor.execute("SELECT * FROM micro_credentials WHERE LOWER(role_id) = LOWER(?)", (role_id,))
    cred_rows = cursor.fetchall()
    micro_creds = []
    for c in cred_rows:
        target_s = c["target_skill"].lower()
        mods_matching = [m for m in sequenced_modules if m.get("skill_name", "").lower() == target_s]
        comp = sum(1 for m in mods_matching if m["status"] == "completed")
        tot = max(1, len(mods_matching))
        micro_creds.append({
            "id": c["id"],
            "code": c["code"],
            "title": c["title"],
            "target_skill": c["target_skill"],
            "estimated_hours": c["estimated_hours"],
            "badge_icon": c["badge_icon"],
            "modules_completed": comp,
            "total_modules": tot,
            "is_earned": (comp >= tot and comp > 0)
        })

    if not micro_creds:
        for idx, m in enumerate(sequenced_modules[:3]):
            micro_creds.append({
                "id": idx + 1,
                "code": f"MC-{role_id[:2].upper()}-{idx+1:02d}",
                "title": f"{m['skill_name']} Micro-Credential",
                "target_skill": m["skill_name"],
                "estimated_hours": m["hours"],
                "badge_icon": "award",
                "modules_completed": 1 if m["status"] == "completed" else 0,
                "total_modules": 1,
                "is_earned": (m["status"] == "completed")
            })

    conn.commit()
    conn.close()

    return {
        "curriculum_id": curr_id,
        "user_id": user_id,
        "target_role_id": role_id,
        "target_role_title": role_title,
        "curriculum_title": curriculum_title,
        "adaptation_version": version,
        "total_estimated_hours": total_hours,
        "weekly_hours": active_weekly_hours,
        "estimated_weeks": estimated_weeks,
        "total_modules": len(sequenced_modules),
        "completed_modules": 0,
        "overall_progress_pct": 0,
        "preferred_difficulty": preferred_difficulty,
        "learning_preferences": learning_preferences,
        "micro_credentials": micro_creds,
        "disclaimer": "Non-Accreditation Notice: Internal micro-credential badges represent competency milestone verification and portfolio evidence. They do not claim official university degrees or accredited third-party certification.",
        "modules": sequenced_modules
    }

def get_active_user_curriculum(user_id: int, target_role_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves active curriculum with updated module progress states."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT uc.*, jr.role_title
    FROM user_curriculums uc
    JOIN job_roles jr ON LOWER(uc.role_id) = LOWER(jr.role_id)
    WHERE uc.user_id = ?
    """
    params = [user_id]
    if target_role_id:
        query += " AND LOWER(uc.role_id) = LOWER(?)"
        params.append(target_role_id)

    query += " ORDER BY uc.id DESC LIMIT 1"
    cursor.execute(query, params)
    curr_row = cursor.fetchone()

    if not curr_row:
        conn.close()
        # Automatically generate personalized pathway
        return generate_personalized_curriculum(user_id=user_id, target_role_id=target_role_id)

    curr_id = curr_row["id"]
    cursor.execute("""
    SELECT * FROM curriculum_modules
    WHERE curriculum_id = ?
    ORDER BY module_order ASC
    """, (curr_id,))
    module_rows = cursor.fetchall()

    modules = []
    completed_skills = set()

    for r in module_rows:
        if r["status"] == "completed":
            completed_skills.add(r["skill_name"].lower() if r["skill_name"] else "")

    for r in module_rows:
        m = dict(r)
        m["module_id"] = r["id"]
        m["prerequisites"] = json.loads(r["prerequisites_json"]) if r["prerequisites_json"] else []
        m["topics"] = json.loads(r["topics_json"]) if r["topics_json"] else []
        m["learning_resources"] = json.loads(r["resources_json"]) if r["resources_json"] else []
        m["practice_activities"] = json.loads(r["practice_json"]) if r["practice_json"] else []
        m["estimated_duration"] = f"{r['hours']} Hours"
        m["assessment"] = r["assessment_info"]
        m["hours"] = r["hours"]

        # Check unlocking
        prereqs = m["prerequisites"]
        if not prereqs or all(p.lower() in completed_skills for p in prereqs):
            m["is_unlocked"] = True
        else:
            m["is_unlocked"] = (r["module_order"] == 1 or r["status"] in ["in_progress", "completed"])

        modules.append(m)

    total_modules = len(modules)
    completed_modules = sum(1 for m in modules if m["status"] == "completed")
    overall_pct = round((completed_modules / total_modules) * 100.0, 1) if total_modules > 0 else 0.0

    # Format micro-credentials
    cursor.execute("SELECT * FROM micro_credentials WHERE LOWER(role_id) = LOWER(?)", (curr_row["role_id"],))
    cred_rows = cursor.fetchall()
    micro_creds = []
    for c in cred_rows:
        target_s = c["target_skill"].lower()
        mods_matching = [m for m in modules if m.get("skill_name", "").lower() == target_s]
        comp = sum(1 for m in mods_matching if m["status"] == "completed")
        tot = max(1, len(mods_matching))
        micro_creds.append({
            "id": c["id"],
            "code": c["code"],
            "title": c["title"],
            "target_skill": c["target_skill"],
            "estimated_hours": c["estimated_hours"],
            "badge_icon": c["badge_icon"],
            "modules_completed": comp,
            "total_modules": tot,
            "is_earned": (comp >= tot and comp > 0)
        })

    if not micro_creds:
        for idx, m in enumerate(modules[:3]):
            micro_creds.append({
                "id": idx + 1,
                "code": f"MC-{curr_row['role_id'][:2].upper()}-{idx+1:02d}",
                "title": f"{m['skill_name']} Micro-Credential",
                "target_skill": m["skill_name"],
                "estimated_hours": m["hours"],
                "badge_icon": "award",
                "modules_completed": 1 if m["status"] == "completed" else 0,
                "total_modules": 1,
                "is_earned": (m["status"] == "completed")
            })

    conn.close()

    return {
        "curriculum_id": curr_id,
        "user_id": user_id,
        "target_role_id": curr_row["role_id"],
        "target_role_title": curr_row["role_title"],
        "curriculum_title": curr_row["title"],
        "adaptation_version": curr_row["adaptation_version"],
        "total_estimated_hours": sum(m["hours"] for m in modules),
        "weekly_hours": curr_row["weekly_hours"] or 10,
        "estimated_weeks": curr_row["estimated_weeks"] or 6,
        "total_modules": total_modules,
        "completed_modules": completed_modules,
        "overall_progress_pct": overall_pct,
        "preferred_difficulty": curr_row["preferred_difficulty"] or "Adaptive",
        "learning_preferences": curr_row["learning_preferences"] or "Hands-on Projects",
        "micro_credentials": micro_creds,
        "disclaimer": "Non-Accreditation Notice: Internal micro-credential badges represent competency milestone verification and portfolio evidence. They do not claim official university degrees or accredited third-party certification.",
        "modules": modules
    }

def update_module_progress(user_id: int, module_id: int, progress_pct: int, status: str) -> Dict[str, Any]:
    """Updates candidate progress and auto-unlocks downstream modules if prerequisites met."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE curriculum_modules
    SET progress_pct = ?, status = ?, completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
    WHERE id = ?
    """, (progress_pct, status, status, module_id))

    cursor.execute("SELECT curriculum_id, skill_name FROM curriculum_modules WHERE id = ?", (module_id,))
    mod_row = cursor.fetchone()
    if mod_row:
        c_id = mod_row["curriculum_id"]
        cursor.execute("SELECT COUNT(*) as completed FROM curriculum_modules WHERE curriculum_id = ? AND status = 'completed'", (c_id,))
        completed_cnt = cursor.fetchone()["completed"]
        cursor.execute("UPDATE user_curriculums SET completed_modules = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (completed_cnt, c_id))

        # Check and unlock downstream modules
        cursor.execute("SELECT * FROM curriculum_modules WHERE curriculum_id = ? ORDER BY module_order ASC", (c_id,))
        all_mods = [dict(m) for m in cursor.fetchall()]
        completed_skills = set(m["skill_name"].lower() for m in all_mods if m["status"] == "completed" and m["skill_name"])

        for m in all_mods:
            prereqs = json.loads(m["prerequisites_json"]) if m["prerequisites_json"] else []
            if m["module_order"] == 1 or not prereqs or all(p.lower() in completed_skills for p in prereqs):
                cursor.execute("UPDATE curriculum_modules SET is_unlocked = 1 WHERE id = ?", (m["id"],))

    conn.commit()
    conn.close()
    return {"module_id": module_id, "status": status, "progress_pct": progress_pct}

