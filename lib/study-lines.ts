/**
 * Short lines shown while something takes a moment (an upload, a recording, a PDF opening, a search, Nova reading):
 * a fact, a quick question with its answer, or a way to study. Plain and checkable, no exclamation marks (ADR-0114).
 * The same list is in lvn-mobile lib/study-lines.ts; keep them identical.
 */
export const STUDY_LINES: readonly string[] = [
  'Binary search halves the range each step, so a million sorted items need at most 20 comparisons.',
  'A hash table finds a key in O(1) on average. Collisions are what make the worst case O(n).',
  'Quick question: what does a stack give back first? The last thing pushed. That is LIFO.',
  'Reviewing after 1, 3 and 7 days keeps more than one long session the night before.',
  'Testing yourself beats rereading. Close the notes and write down what you remember.',
  'TCP guarantees order and delivery. UDP trades that for speed, which is why calls often use it.',
  'A primary key is unique and never null. A foreign key points at one.',
  'Quick question: which traversal of a binary search tree gives sorted order? In-order.',
  "Dijkstra's algorithm breaks on negative edge weights. Bellman-Ford handles them.",
  'Deadlock needs four things at once: mutual exclusion, hold and wait, no preemption, a circular wait.',
  'Big-O ignores constants: 3n and n are both O(n).',
  'Git stores snapshots, and a commit id is a hash of its content and its history.',
  "Merge sort is O(n log n) in every case. Quicksort's worst case is O(n²).",
  'The Pomodoro way: 25 minutes focused, 5 off. After four rounds, take a longer break.',
  'Explaining a topic to someone else shows you quickly what you have not understood.',
  'Quick question: what does ACID stand for? Atomicity, consistency, isolation, durability.',
  'A process has its own memory. Threads inside one process share it.',
  'Third normal form removes transitive dependencies, so a fact is stored in one place.',
  'Sleep is when the brain settles what you learned that day.',
  'Quick question: how long does it take to build a heap from n items? O(n).',
  'DNS turns a name like learnvianotes.in into an IP address before anything else loads.',
  'Recursion needs a base case. Without one, the call stack runs out.',
  'A one-line summary under each page makes revision much faster later.',
  'Quick question: how many edges does a tree with n nodes have? n − 1.',
  'HTTP is stateless. Cookies and tokens are how a server knows you on the next request.',
  'In a linked list, adding at the head is O(1). Reaching the k-th item is O(k).',
  'Mixing related topics in one session helps you tell similar problems apart.',
  'Quick question: what does a compiler do before the program runs? Translates all of it.',
  "Two's complement lets the same adder handle negative numbers.",
  'Doctors, accountants and engineers revise the same way: recall first, then check the notes.',
]

/** What the person is waiting for. Each has its own first line, said plainly. */
export type WaitKind = 'upload' | 'record' | 'pdf' | 'scan' | 'search' | 'nova' | 'general'

/** A starting line that differs between waits, so two loaders on one page do not show the same fact. */
export function firstLine(seed: string): number {
  let h = 0
  for (const c of seed) h = (h * 31 + c.charCodeAt(0)) >>> 0
  return h % STUDY_LINES.length
}
