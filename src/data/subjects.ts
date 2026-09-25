/* ============================================================
   C-NOTE SUBJECTS DATA
   All 13 subjects with metadata.
   Phase 1: metadata only — no real learning content yet.
   ============================================================ */

import type { Subject, SubjectCategory } from '@/types'

/* ── Category registry ────────────────────────────────────── */
export const SUBJECT_CATEGORIES = [
  { id: 'all'     as const, label: 'All',         colorClass: 'cat--all'     },
  { id: 'core-cs' as const, label: 'Core CS',     colorClass: 'cat--core-cs' },
  { id: 'dsa'     as const, label: 'DSA',          colorClass: 'cat--dsa'     },
  { id: 'ai-ml'   as const, label: 'AI & ML',     colorClass: 'cat--ai-ml'   },
  { id: 'tools'   as const, label: 'Tools & APIs', colorClass: 'cat--tools'   },
] as const

export type CategoryId = typeof SUBJECT_CATEGORIES[number]['id']

/* ── Subjects ─────────────────────────────────────────────── */
export const SUBJECTS: Subject[] = [
  {
    id: 'dsa-basics',
    title: 'DSA — Basics',
    shortTitle: 'DSA Basics',
    description: 'Arrays, linked lists, stacks, queues, hashmaps, sorting, searching, and Big O analysis.',
    category: 'dsa' as SubjectCategory,
    lucideIcon: 'Code2',
    topicIds: ['arrays', 'sorting', 'searching', 'recursion', 'stacks-queues'],
    displayTags: ['Arrays', 'Trees', 'Sorting'],
    keywords: 'dsa basics data structures algorithms arrays linked list stack queue hash table binary search linear search big o complexity recursion space time',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'dsa-advanced',
    title: 'DSA — Advanced',
    shortTitle: 'DSA Advanced',
    description: 'Dynamic programming, graphs, segment trees, tries, backtracking, and competitive patterns.',
    category: 'dsa' as SubjectCategory,
    lucideIcon: 'Braces',
    topicIds: ['dynamic-programming', 'graphs', 'advanced-trees', 'tries'],
    displayTags: ['DP', 'Graphs', 'Tries'],
    keywords: 'dsa advanced dynamic programming dp graphs dijkstra segment tree trie backtracking union find segment tree max flow min cut greedy bellman ford',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'sheet-150',
    title: 'Sheet 150',
    shortTitle: 'Sheet 150',
    description: 'All 150 NeetCode problems with problem statements, naive approaches, optimized solutions, and complexity analysis across 12 modules.',
    category: 'dsa' as SubjectCategory,
    lucideIcon: 'ListChecks',
    topicIds: ['arrays', 'strings', 'linked-lists', 'trees', 'graphs', 'dp'],
    displayTags: ['150 Problems', '12 Modules', 'LeetCode'],
    keywords: 'sheet 150 neetcode 150 leetcode dsa recursion backtracking trees graphs binary search dynamic programming intervals greedy tries bit manipulation 12 modules',
    itemCount: 150,
    isActive: true,
  },
  {
    id: 'oops',
    title: 'OOPs',
    shortTitle: 'OOPs',
    description: 'Classes, objects, inheritance, polymorphism, encapsulation, and abstraction with C++ examples.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'Layers',
    topicIds: ['principles', 'design-patterns', 'solid'],
    displayTags: ['Inheritance', 'Patterns', 'SOLID'],
    keywords: 'oops object oriented programming cpp c++ classes inheritance polymorphism encapsulation abstraction solid principles lld design patterns',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'operating-systems',
    title: 'Operating Systems',
    shortTitle: 'OS',
    description: 'Processes, threads, scheduling algorithms, memory management, deadlocks, and file systems.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'Cpu',
    topicIds: ['processes', 'memory-management', 'file-systems', 'concurrency'],
    displayTags: ['Processes', 'Memory', 'Deadlocks'],
    keywords: 'operating systems os threads processes scheduling cpu virtual memory paging deadlocks mutex semaphore file systems inter process communication',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'computer-networks',
    title: 'Computer Networks',
    shortTitle: 'Networks',
    description: 'OSI model, TCP/IP, DNS, HTTP, TLS, routing, congestion control, and WebSockets.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'Network',
    topicIds: ['osi-model', 'tcp-ip', 'application-layer', 'network-security'],
    displayTags: ['OSI Model', 'TCP/IP', 'DNS'],
    keywords: 'computer networks osi model tcp ip dns http https tls routing sockets congestion control web sockets wire protocol',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'dbms',
    title: 'DBMS',
    shortTitle: 'DBMS',
    description: 'Database management: relational model, SQL, normalization, transactions, and indexing.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'Database',
    topicIds: ['relational-model', 'sql', 'normalization', 'transactions'],
    displayTags: ['SQL', 'Normalization', 'Indexes'],
    keywords: 'dbms database management systems sql relational indexing b-tree acid transactions isolation levels normalization concurrency control query optimization postgres mysql',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'system-design',
    title: 'System Design',
    shortTitle: 'System Design',
    description: 'Scalability, reliability, and distributed systems architecture for large-scale platforms.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'Workflow',
    topicIds: ['fundamentals', 'distributed-systems', 'case-studies'],
    displayTags: ['Scalability', 'CAP Theorem', 'Caching'],
    keywords: 'system design hld lsd kafka load balancer caching cap sharding replication consistent hashing rate limiter microservices redis sqs autoscale zero downtime',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'cryptography',
    title: 'Cryptography',
    shortTitle: 'Crypto',
    description: 'Symmetric/asymmetric encryption, hashing, PKI, TLS, and modern cryptographic protocols.',
    category: 'core-cs' as SubjectCategory,
    lucideIcon: 'ShieldCheck',
    topicIds: ['symmetric', 'asymmetric', 'hashing', 'pki'],
    displayTags: ['Encryption', 'Hashing', 'PKI'],
    keywords: 'cryptography encryption aes rsa e2ee asymmetric symmetric hash key management diffie hellman tls digital signature pki security threat model',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'ml-ai',
    title: 'Machine Learning & AI',
    shortTitle: 'ML & AI',
    description: 'ML fundamentals, supervised/unsupervised learning, neural networks, and model evaluation.',
    category: 'ai-ml' as SubjectCategory,
    lucideIcon: 'BrainCircuit',
    topicIds: ['fundamentals', 'supervised', 'unsupervised', 'neural-networks'],
    displayTags: ['Supervised', 'Neural Nets', 'Evaluation'],
    keywords: 'machine learning ai artificial intelligence supervised unsupervised regression classification neural networks feature engineering statistics cross validation model evaluation',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'genai-fluency',
    title: 'GenAI Fluency',
    shortTitle: 'GenAI',
    description: 'LLMs, prompt engineering, RAG, fine-tuning, and responsible AI practices.',
    category: 'ai-ml' as SubjectCategory,
    lucideIcon: 'Sparkles',
    topicIds: ['llm-fundamentals', 'prompt-engineering', 'rag', 'responsible-ai'],
    displayTags: ['LLMs', 'Prompting', 'RAG'],
    keywords: 'genai generative ai llm transformers rag retrieval augmented generation prompt engineering vector database embeddings fine tuning agents attention mechanism',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'api-design',
    title: 'API Design',
    shortTitle: 'API Design',
    description: 'REST, GraphQL, gRPC — principles, versioning, authentication, and documentation.',
    category: 'tools' as SubjectCategory,
    lucideIcon: 'Plug',
    topicIds: ['rest', 'graphql', 'grpc', 'auth'],
    displayTags: ['REST', 'GraphQL', 'gRPC'],
    keywords: 'api design rest graphql grpc openapi swagger rate limiting versioning authentication jwt pagination idempotency',
    itemCount: 0,
    isActive: true,
  },
  {
    id: 'git-github',
    title: 'Git & GitHub',
    shortTitle: 'Git',
    description: 'Version control workflows, branching strategies, collaboration, and CI/CD integration.',
    category: 'tools' as SubjectCategory,
    lucideIcon: 'GitMerge',
    topicIds: ['core-concepts', 'branching', 'collaboration'],
    displayTags: ['Branching', 'Workflows', 'CI/CD'],
    keywords: 'git github version control vcs branching merging pull request rebase stash cherry pick commit reflog conflicts',
    itemCount: 0,
    isActive: true,
  },
]

/* ── Helpers ──────────────────────────────────────────────── */
export const ID_ALIASES: Record<string, string> = {
  s150: 'sheet-150',
  'sheet-150': 'sheet-150',
  sheet_150: 'sheet-150',
  dsab: 'dsa-basics',
  'dsa-basics': 'dsa-basics',
  dsa_basics: 'dsa-basics',
  dsaa: 'dsa-advanced',
  'dsa-advanced': 'dsa-advanced',
  dsa_advanced: 'dsa-advanced',
  os: 'operating-systems',
  'operating-systems': 'operating-systems',
  operating_systems: 'operating-systems',
  cn: 'computer-networks',
  'computer-networks': 'computer-networks',
  computer_networks: 'computer-networks',
  dbms: 'dbms',
  sd: 'system-design',
  'system-design': 'system-design',
  system_design: 'system-design',
  crypto: 'cryptography',
  cryptography: 'cryptography',
  oops: 'oops',
  ml: 'ml-ai',
  'ml-ai': 'ml-ai',
  machine_learning_ai: 'ml-ai',
  genai: 'genai-fluency',
  'genai-fluency': 'genai-fluency',
  genai_fluency: 'genai-fluency',
  api: 'api-design',
  'api-design': 'api-design',
  api_design: 'api-design',
  git: 'git-github',
  'git-github': 'git-github',
  git_github: 'git-github',
}

export const SUBJECT_FOLDER_MAP: Record<string, string> = {
  'sheet-150': 'Sheet 150',
  'dsa-basics': 'dsa_basics',
  'dsa-advanced': 'dsa_advanced',
  oops: 'oops',
  'operating-systems': 'operating_systems',
  'computer-networks': 'computer_networks',
  dbms: 'dbms',
  'system-design': 'system_design',
  cryptography: 'cryptography',
  'ml-ai': 'machine_learning_ai',
  'genai-fluency': 'genai_fluency',
  'api-design': 'api_design',
  'git-github': 'git_github',
}

export function getSubjectById(id: string): Subject | undefined {
  const canonicalId = ID_ALIASES[id] || id
  return SUBJECTS.find((s) => s.id === canonicalId)
}

export function getSubjectContentUrl(subjectId: string, topicId?: string): string {
  const canonicalId = ID_ALIASES[subjectId] || subjectId
  const folder = SUBJECT_FOLDER_MAP[canonicalId]
  if (!folder) return ''

  if (canonicalId === 'sheet-150' && topicId) {
    const topicFileMap: Record<string, string> = {
      arrays: 's150_arrays.html',
      strings: '04_arrays_strings_linkedlists.html#strings',
      'linked-lists': '04_arrays_strings_linkedlists.html#linkedlists',
      linkedlists: '04_arrays_strings_linkedlists.html#linkedlists',
      searching: '07_searching_sorting.html#searching',
      sorting: '07_searching_sorting.html#sorting',
      intervals: '10_intervals.html',
      stack: '06_stack_queue.html#stack',
      queue: '06_stack_queue.html#queue',
      heap: '05_heap_hash.html#heap',
      hash: '05_heap_hash.html#hash',
      recursion: '01_recursion_backtracking.html#recursion',
      backtracking: '01_recursion_backtracking.html#backtracking',
      trees: '02_trees_graphs.html#trees',
      graphs: '02_trees_graphs.html#graphs',
      greedy: '09_greedy.html',
      dp: '03_dynamic_programming.html',
      'dynamic-programming': '03_dynamic_programming.html',
      tries: '08_tries.html',
      'bit-manipulation': '12_bit_manipulation.html',
      math: '11_math_geometry.html',
      'math-geometry': '11_math_geometry.html',
    }
    const filename = topicFileMap[topicId] || `${topicId}.html`
    return `/subjects/${encodeURIComponent(folder)}/${filename}`
  }

  return `/subjects/${encodeURIComponent(folder)}/index.html`
}

export function getSubjectsByCategory(category: SubjectCategory): Subject[] {
  return SUBJECTS.filter((s) => s.category === category)
}

export function getCategoryCount(categoryId: CategoryId): number {
  if (categoryId === 'all') return SUBJECTS.length
  return SUBJECTS.filter((s) => s.category === categoryId).length
}
