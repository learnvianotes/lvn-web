/* ============================================================
   CONTENT PIPELINE — subject registry
   Maps each subject to its legacy HTML source. `order` controls
   the default card order on the landing page; `category` its
   filter group (CATEGORIES).
   ============================================================ */

export const LEGACY_DIR = 'content-src/legacy-html'
export const OUT_DIR = 'content-build'

/**
 * Landing-page filter groups, in display order. Every subject's
 * `category` must be one of these ids.
 */
export const CATEGORIES = [
  { id: 'dsa', title: 'DSA' },
  { id: 'fundamentals', title: 'CS Fundamentals' },
  { id: 'engineering', title: 'Engineering' },
  { id: 'ai', title: 'AI & Data' },
  { id: 'programming', title: 'Programming' },
]

/** @type {Array<{id:string,title:string,description:string,icon:string,category:string,kind:'notes'|'problems',source:string,order:number}>} */
export const SUBJECTS = [
  { id: 'dsa-basics', category: 'dsa', title: 'DSA Basics', icon: 'code', kind: 'notes', source: 'dsa_basics/index.html',
    description: 'Complexity analysis, arrays, linked lists, stacks, queues, hashing, sorting and searching.' },
  { id: 'dsa-advanced', category: 'dsa', title: 'DSA Advanced', icon: 'braces', kind: 'notes', source: 'dsa_advanced/index.html',
    description: 'Recursion, trees, graphs, dynamic programming, tries, segment trees and advanced patterns.' },
  { id: 'sheet-150', category: 'dsa', title: 'Sheet 150', icon: 'list-checks', kind: 'problems', source: 'sheet_150',
    description: '150 curated interview problems with approach, intuition, complexity and optimized code.' },
  { id: 'oops', category: 'fundamentals', title: 'OOPs', icon: 'layers', kind: 'notes', source: 'oops/index.html',
    description: 'Classes, objects, inheritance, polymorphism, encapsulation and abstraction.' },
  { id: 'computer-networks', category: 'fundamentals', title: 'Computer Networks', icon: 'network', kind: 'notes', source: 'computer_networks/index.html',
    description: 'OSI and TCP/IP models, HTTP, DNS, TCP vs UDP, IP addressing, NAT and devices.' },
  { id: 'dbms', category: 'fundamentals', title: 'DBMS', icon: 'database', kind: 'notes', source: 'dbms/index.html',
    description: 'ER model, relational model, SQL, normalization, transactions and indexing.' },
  { id: 'operating-systems', category: 'fundamentals', title: 'Operating Systems', icon: 'cpu', kind: 'notes', source: 'operating_systems/index.html',
    description: 'Processes, threads, scheduling, synchronization, deadlocks and memory management.' },
  { id: 'cryptography', category: 'engineering', title: 'Cryptography', icon: 'shield-check', kind: 'notes', source: 'cryptography/index.html',
    description: 'Symmetric and asymmetric encryption, hashing, key exchange, PKI and E2EE design.' },
  { id: 'system-design', category: 'engineering', title: 'System Design', icon: 'workflow', kind: 'notes', source: 'system_design/index.html',
    description: 'Scalability, caching, databases, queues, consistency and classic design problems.' },
  { id: 'git-github', category: 'engineering', title: 'Git & GitHub', icon: 'git-merge', kind: 'notes', source: 'git_github/index.html',
    description: 'Version control fundamentals, branching, merging, rebasing and remote workflows.' },
  { id: 'api-design', category: 'engineering', title: 'API Design', icon: 'plug', kind: 'notes', source: 'api_design/index.html',
    description: 'REST, GraphQL, gRPC, versioning, pagination, auth and API best practices.' },
  { id: 'artificial-intelligence', category: 'ai', title: 'Artificial Intelligence', icon: 'bot', kind: 'notes', source: 'artificial_intelligence/index.html',
    description: 'Agents, search and A*, games, constraint satisfaction, logic, planning, Bayesian networks, MDPs and reinforcement learning.' },
  { id: 'genai-fluency', category: 'ai', title: 'Generative AI', icon: 'sparkles', kind: 'notes', source: 'genai_fluency/index.html',
    description: 'LLMs, prompting, embeddings, RAG, agents and interview-ready GenAI concepts.' },
  { id: 'ml-ai', category: 'ai', title: 'Machine Learning', icon: 'brain', kind: 'notes', source: 'machine_learning_ai/index.html',
    description: 'Data & features, core concepts, supervised and unsupervised algorithms, evaluation, statistics, MLOps and responsible AI.' },
  { id: 'deep-learning', category: 'ai', title: 'Deep Learning', icon: 'brain-circuit', kind: 'notes', source: 'deep_learning/index.html',
    description: 'Neural networks, backpropagation, optimizers, PyTorch, CNNs, RNNs, attention, Transformers and generative models.' },
  { id: 'data-science', category: 'ai', title: 'Data Science', icon: 'chart', kind: 'notes', source: 'data_science/index.html',
    description: 'Files, NumPy, pandas, web scraping, machine learning with scikit-learn and NLP with NLTK and spaCy.' },
  { id: 'python', category: 'programming', title: 'Python', icon: 'terminal', kind: 'notes', source: 'python/index.html',
    description: 'Syntax, strings, data structures, functions, OOP, generators, the standard library, concurrency, testing and interview prep.' },
  { id: 'c', category: 'programming', title: 'C', icon: 'binary', kind: 'notes', source: 'c/index.html',
    description: 'Types, operators, pointers, memory management, structs, data structures in C, files, the preprocessor and interview prep.' },
  { id: 'cpp', category: 'programming', title: 'C++', icon: 'file-code', kind: 'notes', source: 'cpp/index.html',
    description: 'References, classes, RAII, move semantics, smart pointers, templates, the STL, concurrency and modern C++.' },
  { id: 'java', category: 'programming', title: 'Java', icon: 'coffee', kind: 'notes', source: 'java/index.html',
    description: 'JVM, OOP, strings, exceptions, generics, collections, streams, concurrency, JVM internals and interview prep.' },
  { id: 'javascript', category: 'programming', title: 'JavaScript', icon: 'square-code', kind: 'notes', source: 'javascript/index.html',
    description: 'Types, closures, this, prototypes, classes, the event loop, promises, async/await, modules and interview prep.' },
  { id: 'sql', category: 'programming', title: 'SQL', icon: 'table', kind: 'notes', source: 'sql/index.html',
    description: 'Queries, joins, aggregation, subqueries, CTEs, window functions, indexes, transactions, design and classic interview queries.' },
].map((s, i) => ({ ...s, order: i + 1 }))

/**
 * Sheet 150 categories (NeetCode roadmap order). `match` is compared
 * against the module sidebar section titles in the legacy files.
 */
export const SHEET_150_CATEGORIES = [
  { id: 'arrays-hashing', title: 'Arrays & Hashing', match: /arrays\s*&\s*hashing/i },
  { id: 'two-pointers', title: 'Two Pointers', match: /two pointers/i },
  { id: 'sliding-window', title: 'Sliding Window', match: /sliding window/i },
  { id: 'stack', title: 'Stack', match: /stack/i },
  { id: 'binary-search', title: 'Binary Search', match: /binary search/i },
  { id: 'linked-list', title: 'Linked List', match: /linked list/i },
  { id: 'trees', title: 'Trees', match: /binary trees/i },
  { id: 'tries', title: 'Tries', match: /tries/i },
  { id: 'heap', title: 'Heap / Priority Queue', match: /heap/i },
  { id: 'backtracking', title: 'Backtracking', match: /backtracking/i },
  { id: 'graphs', title: 'Graphs', match: /^\s*2b\.|(?<!advanced )graphs/i },
  { id: 'advanced-graphs', title: 'Advanced Graphs', match: /advanced graphs/i },
  { id: 'dp-1d', title: '1-D Dynamic Programming', match: /1-d dynamic/i },
  { id: 'dp-2d', title: '2-D Dynamic Programming', match: /2-d dynamic/i },
  { id: 'greedy', title: 'Greedy', match: /greedy/i },
  { id: 'intervals', title: 'Intervals', match: /intervals/i },
  { id: 'math-geometry', title: 'Math & Geometry', match: /math/i },
  { id: 'bit-manipulation', title: 'Bit Manipulation', match: /bit manipulation/i },
]

/** Module files, in order. Later files override earlier ones for the same problem id. */
export const SHEET_150_FILES = [
  '01_recursion_backtracking.html',
  '02_trees_graphs.html',
  '03_dynamic_programming.html',
  '04_arrays_strings_linkedlists.html',
  '05_heap_hash.html',
  '06_stack_queue.html',
  '07_searching_sorting.html',
  '08_tries.html',
  '09_greedy.html',
  '10_intervals.html',
  '11_math_geometry.html',
  '12_bit_manipulation.html',
  // Richer rewrite of the first 9 Arrays & Hashing problems — takes precedence.
  's150_arrays.html',
]
