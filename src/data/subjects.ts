/* ============================================================
   C-NOTE MOCK DATA
   Tiny placeholder subjects for Phase 1 UI demonstration only.
   Do NOT replace with real content until Phase 2+.

   The full subject list will be populated from src/data/
   as structured data files — not hardcoded JSX.
   ============================================================ */

import type { Subject } from '@/types'

/**
 * All 13 C-NOTE subjects — metadata only, no content yet.
 * itemCount will be populated when content is added.
 */
export const SUBJECTS: Subject[] = [
  {
    id: 'sheet-150',
    title: 'Sheet 150',
    shortTitle: 'Sheet 150',
    description: 'Curated 150 interview-critical coding problems spanning core data structures and algorithms.',
    topicIds: ['arrays', 'strings', 'linked-lists', 'trees', 'graphs', 'dp'],
    itemCount: 150,
    isActive: false,
  },
  {
    id: 'computer-networks',
    title: 'Computer Networks',
    shortTitle: 'Networks',
    description: 'Networking fundamentals: OSI model, TCP/IP, DNS, HTTP, TLS, and network security.',
    topicIds: ['osi-model', 'tcp-ip', 'application-layer', 'network-security'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'operating-systems',
    title: 'Operating Systems',
    shortTitle: 'OS',
    description: 'Process management, memory, file systems, scheduling, and concurrency.',
    topicIds: ['processes', 'memory-management', 'file-systems', 'concurrency'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'dbms',
    title: 'DBMS',
    shortTitle: 'DBMS',
    description: 'Database management: relational model, SQL, normalization, transactions, and indexing.',
    topicIds: ['relational-model', 'sql', 'normalization', 'transactions'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'oops',
    title: 'OOPs',
    shortTitle: 'OOPs',
    description: 'Object-oriented principles: encapsulation, inheritance, polymorphism, and design patterns.',
    topicIds: ['principles', 'design-patterns', 'solid'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'cryptography',
    title: 'Cryptography',
    shortTitle: 'Crypto',
    description: 'Symmetric/asymmetric encryption, hashing, PKI, and modern cryptographic protocols.',
    topicIds: ['symmetric', 'asymmetric', 'hashing', 'pki'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'system-design',
    title: 'System Design',
    shortTitle: 'System Design',
    description: 'Scalability, reliability, and distributed systems architecture for large-scale platforms.',
    topicIds: ['fundamentals', 'distributed-systems', 'case-studies'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'git-github',
    title: 'Git & GitHub',
    shortTitle: 'Git',
    description: 'Version control workflows, branching strategies, collaboration, and CI/CD integration.',
    topicIds: ['core-concepts', 'branching', 'collaboration'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'api-design',
    title: 'API Design',
    shortTitle: 'API Design',
    description: 'REST, GraphQL, gRPC — principles, versioning, authentication, and documentation.',
    topicIds: ['rest', 'graphql', 'grpc', 'auth'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'dsa-basics',
    title: 'DSA — Basics',
    shortTitle: 'DSA Basics',
    description: 'Core data structures and fundamental algorithms: arrays, sorting, searching, recursion.',
    topicIds: ['arrays', 'sorting', 'searching', 'recursion', 'stacks-queues'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'dsa-advanced',
    title: 'DSA — Advanced',
    shortTitle: 'DSA Advanced',
    description: 'Advanced algorithms: dynamic programming, graphs, trees, tries, segment trees, and more.',
    topicIds: ['dynamic-programming', 'graphs', 'advanced-trees', 'tries'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'ml-ai',
    title: 'Machine Learning & AI',
    shortTitle: 'ML & AI',
    description: 'ML fundamentals, supervised/unsupervised learning, neural networks, and model evaluation.',
    topicIds: ['fundamentals', 'supervised', 'unsupervised', 'neural-networks'],
    itemCount: 0,
    isActive: false,
  },
  {
    id: 'genai-fluency',
    title: 'GenAI Fluency',
    shortTitle: 'GenAI',
    description: 'Generative AI concepts, LLMs, prompt engineering, RAG, and responsible AI practices.',
    topicIds: ['llm-fundamentals', 'prompt-engineering', 'rag', 'responsible-ai'],
    itemCount: 0,
    isActive: false,
  },
]

/** Find a subject by its slug ID */
export function getSubjectById(id: string): Subject | undefined {
  return SUBJECTS.find((s) => s.id === id)
}
