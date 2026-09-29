/* ============================================================
   COURSE MAP — the full curriculum in three areas. A course with
   `subjectId` is already a live catalog subject (it's on the
   landing page); the rest are upcoming and appear under
   "Explore more courses" ("Notify me" records interest — a
   signal for what to build next).
   ============================================================ */

export interface Course {
  id: string
  title: string
  description: string
  /** SubjectIcon name, or a short text badge via `badge` */
  icon?: string
  badge?: string
  /** brand-ish color for the badge */
  color?: string
  /** live catalog subject(s) covering this course */
  subjectId?: string
}

export interface Area {
  id: string
  title: string
  emoji: string
  courses: Course[]
}

export const AREAS: Area[] = [
  {
    id: 'core', title: 'Core Computer Science', emoji: '🧱',
    courses: [
      { id: 'dsa', title: 'Data Structures & Algorithms', icon: 'code', subjectId: 'dsa-basics', description: 'Complexity, arrays to graphs, DP and 150 interview problems.' },
      { id: 'oop', title: 'Object-Oriented Programming', icon: 'layers', subjectId: 'oops', description: 'Classes, inheritance, polymorphism and design principles.' },
      { id: 'dbms', title: 'Database Management Systems', icon: 'database', subjectId: 'dbms', description: 'ER model, SQL, normalization, transactions and indexing.' },
      { id: 'os', title: 'Operating Systems', icon: 'cpu', subjectId: 'operating-systems', description: 'Processes, scheduling, synchronization and memory.' },
      { id: 'cn', title: 'Computer Networks', icon: 'network', subjectId: 'computer-networks', description: 'OSI and TCP/IP, HTTP, DNS, TCP vs UDP and addressing.' },
      { id: 'coa', title: 'Computer Organization & Architecture', icon: 'cpu', description: 'Number systems, CPU design, pipelining, caches and the memory hierarchy.' },
      { id: 'system-design', title: 'System Design', icon: 'workflow', subjectId: 'system-design', description: 'Scalability, caching, queues and classic design problems.' },
      { id: 'software-engineering', title: 'Software Engineering', icon: 'git-merge', description: 'SDLC, agile, testing, design patterns, code review and clean code.' },
      { id: 'security', title: 'Computer Security & Cryptography', icon: 'shield-check', subjectId: 'cryptography', description: 'Encryption, hashing, key exchange and PKI.' },
      { id: 'api-design', title: 'API Design', icon: 'plug', subjectId: 'api-design', description: 'REST, GraphQL, gRPC, versioning and auth.' },
      { id: 'git', title: 'Git & GitHub', icon: 'git-merge', subjectId: 'git-github', description: 'Branching, merging, rebasing and team workflows.' },
    ],
  },
  {
    id: 'ai', title: 'AI & Data', emoji: '🤖',
    courses: [
      { id: 'ai', title: 'Artificial Intelligence', icon: 'bot', subjectId: 'artificial-intelligence', description: 'Search, reasoning, knowledge representation, planning and intelligent agents.' },
      { id: 'machine-learning', title: 'Machine Learning', icon: 'brain', subjectId: 'ml-ai', description: 'Features, classic algorithms, evaluation, statistics and MLOps.' },
      { id: 'deep-learning', title: 'Deep Learning', icon: 'brain-circuit', subjectId: 'deep-learning', description: 'Neural networks, backpropagation, CNNs, RNNs, attention and Transformers.' },
      { id: 'data-science', title: 'Data Science', icon: 'chart', subjectId: 'data-science', description: 'Files, NumPy, pandas, web scraping, machine learning and NLP.' },
      { id: 'genai', title: 'Generative AI', icon: 'sparkles', subjectId: 'genai-fluency', description: 'LLMs, prompting, embeddings, RAG and agents.' },
    ],
  },
  {
    id: 'programming', title: 'Programming', emoji: '💻',
    courses: [
      { id: 'python', title: 'Python', badge: 'Py', color: '#3776ab', subjectId: 'python', description: 'Syntax, data structures, OOP, iterators, generators and interview idioms.' },
      { id: 'cpp', title: 'C++', badge: 'C++', color: '#00599c', subjectId: 'cpp', description: 'STL, pointers, references, memory, templates and competitive-coding tricks.' },
      { id: 'java', title: 'Java', badge: 'Jv', color: '#e76f00', subjectId: 'java', description: 'Collections, OOP, JVM, exceptions, generics and multithreading.' },
      { id: 'javascript', title: 'JavaScript', badge: 'JS', color: '#c9a400', subjectId: 'javascript', description: 'Closures, prototypes, event loop, promises, async/await and ES features.' },
      { id: 'c', title: 'C', badge: 'C', color: '#5c6bc0', subjectId: 'c', description: 'Pointers, arrays, structs, memory management and the compilation model.' },
      { id: 'sql', title: 'SQL', badge: 'SQL', color: '#0f9d8a', subjectId: 'sql', description: 'Joins, grouping, subqueries, window functions and query practice.' },
    ],
  },
]

/** Upcoming courses only (not yet a live subject), per area. */
export function upcomingAreas(live: Set<string>): Area[] {
  return AREAS
    .map((a) => ({ ...a, courses: a.courses.filter((c) => !c.subjectId || !live.has(c.subjectId)) }))
    .filter((a) => a.courses.length)
}
