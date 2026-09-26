/* ============================================================
   CONTENT PIPELINE — subject registry
   Maps each subject to its legacy HTML source. `order` controls
   the card order on the landing page.
   ============================================================ */

export const LEGACY_DIR = 'content-src/legacy-html'
export const OUT_DIR = 'public/content'

/** @type {Array<{id:string,title:string,description:string,icon:string,kind:'notes'|'problems',source:string,order:number}>} */
export const SUBJECTS = [
  { id: 'dsa-basics', title: 'DSA Basics', icon: 'code', kind: 'notes', source: 'dsa_basics/index.html',
    description: 'Complexity analysis, arrays, linked lists, stacks, queues, hashing, sorting and searching.' },
  { id: 'dsa-advanced', title: 'DSA Advanced', icon: 'braces', kind: 'notes', source: 'dsa_advanced/index.html',
    description: 'Recursion, trees, graphs, dynamic programming, tries, segment trees and advanced patterns.' },
  { id: 'sheet-150', title: 'Sheet 150', icon: 'list-checks', kind: 'problems', source: 'sheet_150',
    description: '150 curated interview problems with approach, intuition, complexity and optimized code.' },
  { id: 'oops', title: 'OOPs', icon: 'layers', kind: 'notes', source: 'oops/index.html',
    description: 'Classes, objects, inheritance, polymorphism, encapsulation and abstraction.' },
  { id: 'computer-networks', title: 'Computer Networks', icon: 'network', kind: 'notes', source: 'computer_networks/index.html',
    description: 'OSI and TCP/IP models, HTTP, DNS, TCP vs UDP, IP addressing, NAT and devices.' },
  { id: 'dbms', title: 'DBMS', icon: 'database', kind: 'notes', source: 'dbms/index.html',
    description: 'ER model, relational model, SQL, normalization, transactions and indexing.' },
  { id: 'operating-systems', title: 'Operating Systems', icon: 'cpu', kind: 'notes', source: 'operating_systems/index.html',
    description: 'Processes, threads, scheduling, synchronization, deadlocks and memory management.' },
  { id: 'cryptography', title: 'Cryptography', icon: 'shield-check', kind: 'notes', source: 'cryptography/index.html',
    description: 'Symmetric and asymmetric encryption, hashing, key exchange, PKI and E2EE design.' },
  { id: 'system-design', title: 'System Design', icon: 'workflow', kind: 'notes', source: 'system_design/index.html',
    description: 'Scalability, caching, databases, queues, consistency and classic design problems.' },
  { id: 'git-github', title: 'Git & GitHub', icon: 'git-merge', kind: 'notes', source: 'git_github/index.html',
    description: 'Version control fundamentals, branching, merging, rebasing and remote workflows.' },
  { id: 'api-design', title: 'API Design', icon: 'plug', kind: 'notes', source: 'api_design/index.html',
    description: 'REST, GraphQL, gRPC, versioning, pagination, auth and API best practices.' },
  { id: 'genai-fluency', title: 'GenAI Fluency', icon: 'sparkles', kind: 'notes', source: 'genai_fluency/index.html',
    description: 'LLMs, prompting, embeddings, RAG, agents and interview-ready GenAI concepts.' },
  { id: 'ml-ai', title: 'Machine Learning & AI', icon: 'brain', kind: 'notes', source: 'machine_learning_ai/index.html',
    description: 'Data modeling, training, evaluation, classic algorithms and neural networks.' },
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
