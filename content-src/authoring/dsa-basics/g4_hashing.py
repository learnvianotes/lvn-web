from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Hashing"


@topic(G, "hashing", "Hashing", "hash")
def _():
    yield lead("Hashing turns a key into an array index with a **hash function**, so that search, insert and delete all run in **O(1) on average**. It is the engine behind every dictionary, set, cache and database index you will ever use.")
    yield define("Hashing", "a technique that maps keys from a large *universe* (all integers, all strings …) into a small array called the **hash table** using a hash function `h(key) → 0 … m-1`. The slot `h(key)` is where the key is stored and where it is looked up again.")
    yield flow("Universe of keys", "Hash function h(key)", "Index 0 … m-1", "Hash table slot")
    yield table(
        ["Operation", "Average", "Worst case", "Why"],
        ["`search(key)`", "O(1)", "O(n)", "Compute `h(key)`, look in that slot. Worst case: every key collided into the same slot."],
        ["`insert(key)`", "O(1)", "O(n)", "Same slot computation; the worst case is a full probe sequence or a long chain."],
        ["`delete(key)`", "O(1)", "O(n)", "Find the key as in search, then unlink / mark it."],
    )
    yield note("The O(1) is **average** and relies on a good hash function and a table that is not overfull (low *load factor*, see below). A bad hash function degrades a hash table to a linked list.")

    yield section("What hashing is good for — and what it is not", "apps")
    yield cards(
        ("Dictionaries and sets", "Language containers: Python `dict`/`set`, C++ `unordered_map`, Java `HashMap`, JS `Map`.", "book"),
        ("Database indexing", "Hash indexes answer `WHERE id = 42` without scanning the table.", "database"),
        ("Cryptography", "SHA-256 and friends are hash functions designed so that collisions are infeasible to find.", "lock"),
        ("Caches", "A cache maps a request key to a stored response in O(1) — memoisation, CPU caches, CDNs.", "bolt"),
        ("Symbol tables", "Compilers and interpreters look up every identifier by name in a hash table.", "code"),
        ("Routers", "A router maps a destination address to an output port with a hash lookup.", "route"),
        cols=3,
    )
    yield warn("Hashing is **not** the right tool when you need order: finding the *closest* value, the *k*-th smallest, a sorted traversal, or *prefix* searches (use a Trie) and range queries (use a balanced BST / sorted array). A hash table scatters keys deliberately, so neighbouring keys end up far apart.")

    yield section("Direct address table", "table")
    yield p("Suppose there are at most 1000 keys and every key is an integer between 0 and 999. The simplest O(1) structure is a boolean (or value) array of size 1000 where the key **is** the index: `table[key] = true` inserts, `table[key]` searches, `table[key] = false` deletes.")
    yield diagram('''
        key:    0     1     2     3     4     5     6     7     8     9
              ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
              │  T  │  F  │  F  │  T  │  F  │  F  │  F  │  T  │  F  │  F  │
              └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
        after insert(0), insert(3), insert(7) — the key is the index, no hash function at all
    ''', "A direct address table for keys 0–9")
    yield multi('''
        search 3: true
        search 5: false
        after delete 3 → search 3: false
    ''', py='''
        table = [False] * 10          # keys 0..9, the key itself is the index

        def insert(k): table[k] = True
        def delete(k): table[k] = False
        def search(k): return table[k]

        for k in (0, 3, 7):
            insert(k)
        print("search 3:", "true" if search(3) else "false")
        print("search 5:", "true" if search(5) else "false")
        delete(3)
        print("after delete 3 → search 3:", "true" if search(3) else "false")
    ''', cpp='''
        #include <iostream>
        using namespace std;

        bool table[10] = {false};     // keys 0..9, the key itself is the index

        void insertKey(int k) { table[k] = true; }
        void deleteKey(int k) { table[k] = false; }
        bool search(int k) { return table[k]; }

        int main() {
            for (int k : {0, 3, 7}) insertKey(k);
            cout << "search 3: " << (search(3) ? "true" : "false") << "\\n";
            cout << "search 5: " << (search(5) ? "true" : "false") << "\\n";
            deleteKey(3);
            cout << "after delete 3 → search 3: " << (search(3) ? "true" : "false") << "\\n";
        }
    ''', java='''
        public class Main {
            static boolean[] table = new boolean[10];   // keys 0..9, the key itself is the index

            static void insert(int k) { table[k] = true; }
            static void delete(int k) { table[k] = false; }
            static boolean search(int k) { return table[k]; }

            public static void main(String[] args) {
                for (int k : new int[]{0, 3, 7}) insert(k);
                System.out.println("search 3: " + search(3));
                System.out.println("search 5: " + search(5));
                delete(3);
                System.out.println("after delete 3 → search 3: " + search(3));
            }
        }
    ''', js='''
        const table = new Array(10).fill(false);   // keys 0..9, the key itself is the index

        const insert = (k) => { table[k] = true; };
        const del = (k) => { table[k] = false; };
        const search = (k) => table[k];

        for (const k of [0, 3, 7]) insert(k);
        console.log("search 3:", search(3));
        console.log("search 5:", search(5));
        del(3);
        console.log("after delete 3 → search 3:", search(3));
    ''')
    yield complexity("O(1) per operation", "O(size of key universe)")
    yield bad("The direct address table **cannot handle large or non-integer keys**: 10-digit phone numbers would need a 10-billion-slot array, and strings have no natural index at all. Hashing fixes this by *compressing* the key universe into a small range `0 … m-1`.")

    yield section("Hash functions", "math-function")
    yield p("A hash function `h` converts a key into a slot index. A good one has four properties:")
    yield ol(
        "**Deterministic** — the same key must always map to the same slot, or we could never find it again.",
        "**In range** — produces values in `0 … m-1` where `m` is the table size.",
        "**Fast** — O(1) for integers and O(len) for a string of length `len`.",
        "**Uniform** — spreads keys evenly across the slots, so that chains and probe sequences stay short.",
    )
    yield table(
        ["Key type", "Typical hash function", "Note"],
        ["Integer", "`h(key) = key % m`", "Choose `m` **prime** and not close to a power of 2, so patterns in the keys (even numbers, multiples of 10) do not pile up in a few slots."],
        ["String", "Weighted (polynomial) sum: `h = (h · 31 + c) % m` over the characters", "Plain sum of character codes is bad: `\"abc\"`, `\"bca\"`, `\"cab\"` would all collide. The weight makes position matter."],
        ["Any", "**Universal hashing**: pick `h` at random from a family of functions at start-up", "No fixed input can be adversarially chosen to collide, because the attacker does not know which function was picked."],
    )
    yield multi('''
        abc → 33
        cab → 80
        bca → 53
        hash → 67
    ''', py='''
        def string_hash(s, m):
            h = 0
            for ch in s:
                h = (h * 31 + ord(ch)) % m    # weighted sum: position matters
            return h

        M = 97                                # a prime table size
        for s in ["abc", "cab", "bca", "hash"]:
            print(s, "→", string_hash(s, M))
    ''', cpp='''
        #include <iostream>
        #include <string>
        using namespace std;

        int stringHash(const string& s, int m) {
            long long h = 0;
            for (char ch : s)
                h = (h * 31 + ch) % m;        // weighted sum: position matters
            return (int)h;
        }

        int main() {
            const int M = 97;                 // a prime table size
            for (string s : {"abc", "cab", "bca", "hash"})
                cout << s << " → " << stringHash(s, M) << "\\n";
        }
    ''', java='''
        public class Main {
            static int stringHash(String s, int m) {
                long h = 0;
                for (char ch : s.toCharArray())
                    h = (h * 31 + ch) % m;    // weighted sum: position matters
                return (int) h;
            }

            public static void main(String[] args) {
                final int M = 97;             // a prime table size
                for (String s : new String[]{"abc", "cab", "bca", "hash"})
                    System.out.println(s + " → " + stringHash(s, M));
            }
        }
    ''', js='''
        function stringHash(s, m) {
            let h = 0;
            for (const ch of s)
                h = (h * 31 + ch.charCodeAt(0)) % m;   // weighted sum: position matters
            return h;
        }

        const M = 97;                                  // a prime table size
        for (const s of ["abc", "cab", "bca", "hash"])
            console.log(s, "→", stringHash(s, M));
    ''')
    yield complexity("O(len) per string", "O(1)")
    yield note("Java's `String.hashCode()` is exactly this polynomial with base 31 (without the modulo); Python and JavaScript engines use randomised variants so that attackers cannot pre-compute colliding keys.")

    yield section("Collisions and how to handle them", "arrows-shuffle")
    yield define("Collision", "two different keys hashing to the same slot: `h(k1) == h(k2)` with `k1 != k2`. With more possible keys than slots, collisions are unavoidable (pigeonhole principle) — a hash table design is mostly a decision about what to do when they happen.")
    yield cards(
        ("Perfect hashing", "If **all keys are known in advance** (keywords of a programming language, a fixed set of country codes) a collision-free function can be constructed offline. Not possible for dynamic data.", "target"),
        ("Chaining", "Each slot holds a **list** of all keys that hashed there. The table never fills up.", "link"),
        ("Open addressing", "All keys live **inside the array**. On a collision, probe other slots in a fixed order until an empty one is found: linear probing, quadratic probing or double hashing.", "grid-dots"),
        cols=3,
    )

    yield section("Chaining", "link")
    yield p("The table is an array of `m` list heads. `insert` appends to the list at `h(key)`, `search` and `delete` walk that one list only. With `h(key) = key % 7` and the keys `50, 21, 58, 17, 15, 49, 56, 22, 23, 25`:")
    yield diagram('''
        slot
         0  │ 21 │──▶│ 49 │──▶│ 56 │          21 % 7 = 0, 49 % 7 = 0, 56 % 7 = 0
         1  │ 50 │──▶│ 15 │──▶│ 22 │          50 % 7 = 1, 15 % 7 = 1, 22 % 7 = 1
         2  │ 58 │──▶│ 23 │                   58 % 7 = 2, 23 % 7 = 2
         3  │ 17 │
         4  │ 25 │
         5  │    │
         6  │    │
        hash table = array of linked-list heads
    ''', "Chaining with m = 7: every slot owns the chain of keys that hashed to it")
    yield p("**Performance.** Let `m` be the number of slots and `n` the number of keys. The **load factor** `α = n / m` is the expected chain length under uniform hashing, so:")
    yield formula("expected search / delete time = O(1 + α)   —   O(1) to hash, O(α) to walk the chain")
    yield p("Keeping `α` bounded by a constant (Java's `HashMap` rehashes at `α = 0.75`) makes every operation O(1) on average. Chains can be stored in any of these:")
    yield table(
        ["Chain structure", "Pros", "Cons"],
        ["Linked list", "O(1) insert at head, no resizing", "Poor cache locality, one pointer per key"],
        ["Dynamic array (`vector`, `ArrayList`, Python `list`)", "Cache friendly, simple", "Delete from the middle shifts elements (chains are short, so it hardly matters)"],
        ["Self-balancing BST (AVL, Red-Black)", "Worst case per chain drops to O(log n) — Java 8+ `HashMap` switches a bucket to a tree when it grows past 8 entries", "Heavier nodes, more code"],
    )
    yield io("buckets = 7; insert 70, 71, 9, 56, 72; delete 56; search 9, 93", "9 → true, 93 → false")
    yield multi('''
        0: 70 56
        1: 71
        2: 9 72
        3:
        4:
        5:
        6:
        after delete 56
        0: 70
        1: 71
        2: 9 72
        3:
        4:
        5:
        6:
        search 9: true
        search 93: false
    ''', py='''
        class ChainedHash:
            def __init__(self, buckets):
                self.buckets = buckets
                self.table = [[] for _ in range(buckets)]   # one list per slot

            def _h(self, key):
                return key % self.buckets

            def insert(self, key):
                self.table[self._h(key)].append(key)        # O(1): append to the chain

            def delete(self, key):
                chain = self.table[self._h(key)]
                if key in chain:
                    chain.remove(key)                       # O(chain length)

            def search(self, key):
                return key in self.table[self._h(key)]      # walk one chain only

            def show(self):
                for i, chain in enumerate(self.table):
                    print(f"{i}:", *chain)

        h = ChainedHash(7)
        for k in (70, 71, 9, 56, 72):
            h.insert(k)
        h.show()
        h.delete(56)
        print("after delete 56")
        h.show()
        print("search 9:", "true" if h.search(9) else "false")
        print("search 93:", "true" if h.search(93) else "false")
    ''', cpp='''
        #include <iostream>
        #include <list>
        #include <vector>
        #include <algorithm>
        using namespace std;

        class ChainedHash {
            int buckets;
            vector<list<int>> table;                        // one linked list per slot
            int h(int key) const { return key % buckets; }
        public:
            ChainedHash(int b) : buckets(b), table(b) {}
            void insert(int key) { table[h(key)].push_back(key); }       // O(1)
            void remove(int key) { table[h(key)].remove(key); }          // O(chain length)
            bool search(int key) const {
                const list<int>& chain = table[h(key)];
                return find(chain.begin(), chain.end(), key) != chain.end();
            }
            void show() const {
                for (int i = 0; i < buckets; i++) {
                    cout << i << ":";
                    for (int k : table[i]) cout << " " << k;
                    cout << "\\n";
                }
            }
        };

        int main() {
            ChainedHash h(7);
            for (int k : {70, 71, 9, 56, 72}) h.insert(k);
            h.show();
            h.remove(56);
            cout << "after delete 56\\n";
            h.show();
            cout << "search 9: " << (h.search(9) ? "true" : "false") << "\\n";
            cout << "search 93: " << (h.search(93) ? "true" : "false") << "\\n";
        }
    ''', java='''
        import java.util.LinkedList;

        public class Main {
            static class ChainedHash {
                int buckets;
                LinkedList<Integer>[] table;                 // one linked list per slot

                @SuppressWarnings("unchecked")
                ChainedHash(int b) {
                    buckets = b;
                    table = new LinkedList[b];
                    for (int i = 0; i < b; i++) table[i] = new LinkedList<>();
                }
                int h(int key) { return key % buckets; }
                void insert(int key) { table[h(key)].add(key); }                 // O(1)
                void delete(int key) { table[h(key)].remove(Integer.valueOf(key)); }   // O(chain length)
                boolean search(int key) { return table[h(key)].contains(key); }
                void show() {
                    for (int i = 0; i < buckets; i++) {
                        StringBuilder sb = new StringBuilder(i + ":");
                        for (int k : table[i]) sb.append(" ").append(k);
                        System.out.println(sb);
                    }
                }
            }

            public static void main(String[] args) {
                ChainedHash h = new ChainedHash(7);
                for (int k : new int[]{70, 71, 9, 56, 72}) h.insert(k);
                h.show();
                h.delete(56);
                System.out.println("after delete 56");
                h.show();
                System.out.println("search 9: " + h.search(9));
                System.out.println("search 93: " + h.search(93));
            }
        }
    ''', js='''
        class ChainedHash {
            constructor(buckets) {
                this.buckets = buckets;
                this.table = Array.from({ length: buckets }, () => []);   // one list per slot
            }
            h(key) { return key % this.buckets; }
            insert(key) { this.table[this.h(key)].push(key); }            // O(1)
            delete(key) {
                const chain = this.table[this.h(key)];
                const at = chain.indexOf(key);
                if (at !== -1) chain.splice(at, 1);                       // O(chain length)
            }
            search(key) { return this.table[this.h(key)].includes(key); }
            show() {
                this.table.forEach((chain, i) => console.log(`${i}:` + chain.map(k => " " + k).join("")));
            }
        }

        const h = new ChainedHash(7);
        for (const k of [70, 71, 9, 56, 72]) h.insert(k);
        h.show();
        h.delete(56);
        console.log("after delete 56");
        h.show();
        console.log("search 9:", h.search(9));
        console.log("search 93:", h.search(93));
    ''')
    yield complexity("O(1 + α) average, O(n) worst", "O(n + m)")

    yield section("Load factor and rehashing", "scale")
    yield define("Load factor α", "`n / m` — the number of stored keys divided by the number of slots. It measures how full the table is and directly controls the cost of every operation.")
    yield diagram('''
        empty table, 10 slots         [_, _, _, _, _, _, _, _, _, _]                        α = 0.0
        after 5 insertions            [x, x, x, x, x, _, _, _, _, _]                        α = 0.5
        after 10 insertions           [x, x, x, x, x, x, x, x, x, x]                        α = 1.0  (full)
        rehash to 20 slots, insert    [x, x, x, x, x, x, x, x, x, x, x, _, _, _, _, _, _, _, _, _]   α = 0.55
    ''', "The load factor grows with every insert and drops when the table is resized")
    yield p("**Rehashing**: when `α` crosses a threshold (typically 0.75 for chaining, 0.5 for open addressing), allocate a new table about twice as large and re-insert every key with the *new* `h` — the slot of a key depends on `m`, so the old positions are useless. One rehash costs O(n), but it happens only after O(n) cheap inserts, so insertion stays **amortised O(1)**.")
    yield table(
        ["Scheme", "Expected successful search", "Expected unsuccessful search / insert", "Must keep"],
        ["Chaining", "O(1 + α)", "O(1 + α)", "`α` bounded by a constant (any value works, even `α > 1`)"],
        ["Open addressing", "about `1/α · ln(1/(1-α))`", "about `1 / (1 - α)`", "`α < 1`, in practice `α ≤ 0.5 … 0.7`"],
    )
    yield note("Read the open-addressing formula at `α = 0.5`: an unsuccessful search probes about 2 slots; at `α = 0.9` about 10. Performance degrades sharply as the table fills, which is why open-addressing tables resize early.")

    yield section("Open addressing — linear probing", "grid-dots")
    yield p("In open addressing there are no chains: **every key lives in the array itself**, so the number of slots must be `>=` the number of keys. On a collision we *probe* — try other slots in a fixed sequence until an empty one appears. Because all data is in one contiguous array, this is very **cache friendly**.")
    yield formula("linear probing:   hash(key, i) = (h(key) + i) % m   for i = 0, 1, 2, …")
    yield p("With `m = 7`, `h(key) = key % 7` and the keys `50, 51, 49, 16, 56, 15, 19`:")
    yield diagram('''
        key   h(key)   placed at                    0 │ 49 │
         50     1      1                            1 │ 50 │
         51     2      2                            2 │ 51 │
         49     0      0                            3 │ 16 │  ← 2 taken, moved to 3
         16     2      3   (2 taken)                4 │ 56 │  ← 0,1,2,3 taken, moved to 4
         56     0      4   (0,1,2,3 taken)          5 │ 15 │  ← 1,2,3,4 taken, moved to 5
         15     1      5   (1,2,3,4 taken)          6 │ 19 │  ← 5 taken, moved to 6
         19     5      6   (5 taken)
    ''', "Linear probing: each collision slides to the next free slot (wrapping around at the end)")
    yield cards(
        ("Searching", "Compute `h(key)` and compare. If the slot holds another key, keep moving to the next slot. Stop with *not found* when you hit an **empty** slot or come back to the start index.", "search"),
        ("Deleting", "**Never simply empty the slot.** An empty slot ends every search passing through it, so keys that were probed past this slot would become unreachable. Instead write a special **DELETED** marker: search skips over it, insert may reuse it.", "trash"),
        ("Inserting", "Probe from `h(key)` until an empty *or deleted* slot; fail if the table is full or the key already exists (search first).", "plus"),
        cols=3,
    )
    yield define("Primary clustering", "the phenomenon where keys that hash to the same **or nearby** slots form long runs of occupied slots. Any key hashing into a cluster lands at its end and makes it longer, so clusters grow faster and faster — search, insert and delete all degrade towards O(n). Linear probing suffers from it most.")

    yield section("Quadratic probing and double hashing", "arrows-shuffle")
    yield p("Both break clusters by making the probe sequence depend on something other than `+1`:")
    yield table(
        ["Scheme", "Probe sequence", "Clustering", "Guarantee"],
        ["Linear probing", "`(h(key) + i) % m`", "Primary clustering", "Always finds a free slot if one exists"],
        ["Quadratic probing", "`(h(key) + i²) % m`", "Secondary clustering (keys with the same `h` still share a sequence)", "Guaranteed to find a free slot only if `m` is prime and `α < 0.5`"],
        ["Double hashing", "`(h1(key) + i · h2(key)) % m`", "None — different keys with the same `h1` almost always get different step sizes", "Finds a free slot if one exists when `h2(key)` is **relatively prime to `m`** (e.g. `m` prime and `h2(key) = 1 + key % (m-1)`)"],
    )
    yield p("Double hashing distributes keys more uniformly than linear and quadratic probing and is the closest practical approximation to the *uniform hashing* assumption behind the `1 / (1 - α)` analysis. The insert routine from the notes:")
    yield steps(
        ("Reject a full table", "If `n == m` return an error — open addressing cannot store more keys than slots."),
        ("Compute the start and the step", "`probe = h1(key)`, `offset = h2(key)`."),
        ("Walk the sequence", "While `table[probe]` is occupied: `probe = (probe + offset) % m`."),
        ("Store", "`table[probe] = key`."),
    )
    yield io("m = 7, h1 = key % 7, h2 = 1 + key % 6; insert 50, 51, 49, 16, 56, 15, 19", "slots 0..6: 49 50 51 56 19 16 15")
    yield multi('''
        insert 50: h1=1 → slot 1
        insert 51: h1=2 → slot 2
        insert 49: h1=0 → slot 0
        insert 16: h1=2 → slot 5
        insert 56: h1=0 → slot 3
        insert 15: h1=1 → slot 6
        insert 19: h1=5 → slot 4
        table: 49 50 51 56 19 16 15
    ''', py='''
        M = 7
        table = [None] * M

        def h1(key): return key % M
        def h2(key): return 1 + key % (M - 1)        # 1..6, all relatively prime to 7

        def double_hashing_insert(key):
            probe, offset = h1(key), h2(key)
            while table[probe] is not None:
                probe = (probe + offset) % M          # jump by the key's own step size
            table[probe] = key
            print(f"insert {key}: h1={h1(key)} → slot {probe}")

        for k in (50, 51, 49, 16, 56, 15, 19):
            double_hashing_insert(k)
        print("table:", *table)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        const int M = 7;
        int table_[M];
        bool used[M] = {false};

        int h1(int key) { return key % M; }
        int h2(int key) { return 1 + key % (M - 1); }   // 1..6, all relatively prime to 7

        void doubleHashingInsert(int key) {
            int probe = h1(key), offset = h2(key);
            while (used[probe])
                probe = (probe + offset) % M;            // jump by the key's own step size
            table_[probe] = key; used[probe] = true;
            cout << "insert " << key << ": h1=" << h1(key) << " → slot " << probe << "\\n";
        }

        int main() {
            for (int k : {50, 51, 49, 16, 56, 15, 19}) doubleHashingInsert(k);
            cout << "table:";
            for (int i = 0; i < M; i++) cout << " " << table_[i];
            cout << "\\n";
        }
    ''', java='''
        public class Main {
            static final int M = 7;
            static Integer[] table = new Integer[M];

            static int h1(int key) { return key % M; }
            static int h2(int key) { return 1 + key % (M - 1); }   // 1..6, all relatively prime to 7

            static void doubleHashingInsert(int key) {
                int probe = h1(key), offset = h2(key);
                while (table[probe] != null)
                    probe = (probe + offset) % M;                  // jump by the key's own step size
                table[probe] = key;
                System.out.println("insert " + key + ": h1=" + h1(key) + " → slot " + probe);
            }

            public static void main(String[] args) {
                for (int k : new int[]{50, 51, 49, 16, 56, 15, 19}) doubleHashingInsert(k);
                StringBuilder sb = new StringBuilder("table:");
                for (Integer v : table) sb.append(" ").append(v);
                System.out.println(sb);
            }
        }
    ''', js='''
        const M = 7;
        const table = new Array(M).fill(null);

        const h1 = (key) => key % M;
        const h2 = (key) => 1 + key % (M - 1);          // 1..6, all relatively prime to 7

        function doubleHashingInsert(key) {
            let probe = h1(key);
            const offset = h2(key);
            while (table[probe] !== null)
                probe = (probe + offset) % M;            // jump by the key's own step size
            table[probe] = key;
            console.log(`insert ${key}: h1=${h1(key)} → slot ${probe}`);
        }

        for (const k of [50, 51, 49, 16, 56, 15, 19]) doubleHashingInsert(k);
        console.log("table:", table.join(" "));
    ''')
    yield complexity("O(1 / (1 - α)) expected per insert", "O(m)")
    yield pitfall("`h2(key)` must never be 0 (the probe would stay in place forever) and must be relatively prime to `m`, otherwise the sequence visits only a fraction of the slots and can miss free ones. `m` prime with `h2 = 1 + key % (m - 1)` satisfies both.")

    yield section("Implementation of open addressing", "code")
    yield p("A complete linear-probing table with the DELETED marker. Empty slots are `-1`, deleted slots `-2`; keys are assumed non-negative. `insert` refuses duplicates and reuses deleted slots; `search` skips deleted slots and stops at an empty one.")
    yield io("capacity = 7; insert 70, 71, 9, 56, 72; delete 9; search 9, 56; insert 56 again", "search 9 → false, search 56 → true, insert 56 → false (duplicate)")
    yield multi('''
        70 71 9 56 72 _ _
        search 9: true
        delete 9: true
        70 71 x 56 72 _ _
        search 9: false
        search 56: true
        insert 56 again: false
    ''', py='''
        EMPTY, DELETED = -1, -2

        class OpenHash:
            def __init__(self, capacity):
                self.cap = capacity
                self.table = [EMPTY] * capacity
                self.size = 0

            def _h(self, key):
                return key % self.cap

            def search(self, key):
                h = i = self._h(key)
                while self.table[i] != EMPTY:            # a DELETED slot does NOT stop the search
                    if self.table[i] == key:
                        return True
                    i = (i + 1) % self.cap
                    if i == h:                           # wrapped all the way round
                        return False
                return False

            def insert(self, key):
                if self.size == self.cap or self.search(key):
                    return False
                h = i = self._h(key)
                while self.table[i] not in (EMPTY, DELETED):   # a DELETED slot can be reused
                    i = (i + 1) % self.cap
                    if i == h:
                        return False
                self.table[i] = key
                self.size += 1
                return True

            def delete(self, key):
                h = i = self._h(key)
                while self.table[i] != EMPTY:
                    if self.table[i] == key:
                        self.table[i] = DELETED          # mark, never empty the slot
                        self.size -= 1
                        return True
                    i = (i + 1) % self.cap
                    if i == h:
                        return False
                return False

            def show(self):
                print(*["_" if v == EMPTY else "x" if v == DELETED else v for v in self.table])

        def b(x): return "true" if x else "false"

        t = OpenHash(7)
        for k in (70, 71, 9, 56, 72):
            t.insert(k)
        t.show()
        print("search 9:", b(t.search(9)))
        print("delete 9:", b(t.delete(9)))
        t.show()
        print("search 9:", b(t.search(9)))
        print("search 56:", b(t.search(56)))
        print("insert 56 again:", b(t.insert(56)))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        const int EMPTY = -1, DELETED = -2;

        class OpenHash {
            int cap, size = 0;
            vector<int> table;
            int h(int key) const { return key % cap; }
        public:
            OpenHash(int c) : cap(c), table(c, EMPTY) {}

            bool search(int key) const {
                int start = h(key), i = start;
                while (table[i] != EMPTY) {              // a DELETED slot does NOT stop the search
                    if (table[i] == key) return true;
                    i = (i + 1) % cap;
                    if (i == start) return false;        // wrapped all the way round
                }
                return false;
            }
            bool insert(int key) {
                if (size == cap || search(key)) return false;
                int start = h(key), i = start;
                while (table[i] != EMPTY && table[i] != DELETED) {   // a DELETED slot can be reused
                    i = (i + 1) % cap;
                    if (i == start) return false;
                }
                table[i] = key; size++;
                return true;
            }
            bool remove(int key) {
                int start = h(key), i = start;
                while (table[i] != EMPTY) {
                    if (table[i] == key) { table[i] = DELETED; size--; return true; }   // mark, never empty
                    i = (i + 1) % cap;
                    if (i == start) return false;
                }
                return false;
            }
            void show() const {
                for (int i = 0; i < cap; i++) {
                    if (i) cout << " ";
                    if (table[i] == EMPTY) cout << "_"; else if (table[i] == DELETED) cout << "x"; else cout << table[i];
                }
                cout << "\\n";
            }
        };

        const char* b(bool x) { return x ? "true" : "false"; }

        int main() {
            OpenHash t(7);
            for (int k : {70, 71, 9, 56, 72}) t.insert(k);
            t.show();
            cout << "search 9: " << b(t.search(9)) << "\\n";
            cout << "delete 9: " << b(t.remove(9)) << "\\n";
            t.show();
            cout << "search 9: " << b(t.search(9)) << "\\n";
            cout << "search 56: " << b(t.search(56)) << "\\n";
            cout << "insert 56 again: " << b(t.insert(56)) << "\\n";
        }
    ''', java='''
        public class Main {
            static final int EMPTY = -1, DELETED = -2;

            static class OpenHash {
                int cap, size = 0;
                int[] table;
                OpenHash(int c) { cap = c; table = new int[c]; java.util.Arrays.fill(table, EMPTY); }
                int h(int key) { return key % cap; }

                boolean search(int key) {
                    int start = h(key), i = start;
                    while (table[i] != EMPTY) {              // a DELETED slot does NOT stop the search
                        if (table[i] == key) return true;
                        i = (i + 1) % cap;
                        if (i == start) return false;        // wrapped all the way round
                    }
                    return false;
                }
                boolean insert(int key) {
                    if (size == cap || search(key)) return false;
                    int start = h(key), i = start;
                    while (table[i] != EMPTY && table[i] != DELETED) {   // a DELETED slot can be reused
                        i = (i + 1) % cap;
                        if (i == start) return false;
                    }
                    table[i] = key; size++;
                    return true;
                }
                boolean delete(int key) {
                    int start = h(key), i = start;
                    while (table[i] != EMPTY) {
                        if (table[i] == key) { table[i] = DELETED; size--; return true; }   // mark, never empty
                        i = (i + 1) % cap;
                        if (i == start) return false;
                    }
                    return false;
                }
                void show() {
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < cap; i++) {
                        if (i > 0) sb.append(" ");
                        sb.append(table[i] == EMPTY ? "_" : table[i] == DELETED ? "x" : String.valueOf(table[i]));
                    }
                    System.out.println(sb);
                }
            }

            public static void main(String[] args) {
                OpenHash t = new OpenHash(7);
                for (int k : new int[]{70, 71, 9, 56, 72}) t.insert(k);
                t.show();
                System.out.println("search 9: " + t.search(9));
                System.out.println("delete 9: " + t.delete(9));
                t.show();
                System.out.println("search 9: " + t.search(9));
                System.out.println("search 56: " + t.search(56));
                System.out.println("insert 56 again: " + t.insert(56));
            }
        }
    ''', js='''
        const EMPTY = -1, DELETED = -2;

        class OpenHash {
            constructor(capacity) {
                this.cap = capacity;
                this.table = new Array(capacity).fill(EMPTY);
                this.size = 0;
            }
            h(key) { return key % this.cap; }

            search(key) {
                const start = this.h(key);
                let i = start;
                while (this.table[i] !== EMPTY) {            // a DELETED slot does NOT stop the search
                    if (this.table[i] === key) return true;
                    i = (i + 1) % this.cap;
                    if (i === start) return false;           // wrapped all the way round
                }
                return false;
            }
            insert(key) {
                if (this.size === this.cap || this.search(key)) return false;
                const start = this.h(key);
                let i = start;
                while (this.table[i] !== EMPTY && this.table[i] !== DELETED) {   // a DELETED slot can be reused
                    i = (i + 1) % this.cap;
                    if (i === start) return false;
                }
                this.table[i] = key; this.size++;
                return true;
            }
            delete(key) {
                const start = this.h(key);
                let i = start;
                while (this.table[i] !== EMPTY) {
                    if (this.table[i] === key) { this.table[i] = DELETED; this.size--; return true; }   // mark, never empty
                    i = (i + 1) % this.cap;
                    if (i === start) return false;
                }
                return false;
            }
            show() {
                console.log(this.table.map(v => v === EMPTY ? "_" : v === DELETED ? "x" : v).join(" "));
            }
        }

        const t = new OpenHash(7);
        for (const k of [70, 71, 9, 56, 72]) t.insert(k);
        t.show();
        console.log("search 9:", t.search(9));
        console.log("delete 9:", t.delete(9));
        t.show();
        console.log("search 9:", t.search(9));
        console.log("search 56:", t.search(56));
        console.log("insert 56 again:", t.insert(56));
    ''')
    yield complexity("O(1) average, O(n) worst", "O(m)")
    yield pitfall("Walk through `search 56` after `delete 9`: `h(56) = 0` → slot 0 holds 70, slot 1 holds 71, slot 2 is DELETED (skip!), slot 3 holds 56 → found. Had `delete` emptied slot 2 instead, the search would have stopped there and reported 56 as missing even though it is in the table.")

    yield section("Chaining vs open addressing", "scale")
    yield table(
        ["", "Chaining", "Open addressing"],
        ["Table full?", "Never — chains simply grow", "Yes; resizing becomes mandatory"],
        ["Sensitivity to hash function", "Low — a poor function only lengthens chains", "High — clustering needs extra care"],
        ["Cache performance", "Poor: chain nodes are scattered in memory", "Good: everything is in one array"],
        ["Extra space", "One link pointer per key", "Empty slots must be kept (`α` well below 1) to achieve the same performance"],
        ["Deletion", "Unlink from the chain", "Needs the DELETED marker"],
        ["Unsuccessful search cost", "`1 + α`", "`1 / (1 - α)`"],
    )

    yield section("Problem: frequencies of array elements", "chart-bar")
    yield io("arr = [10, 12, 10, 15, 10, 20, 12, 12]", "10 3 / 12 3 / 15 1 / 20 1")
    yield p("**Naive approach** — for every element, skip it if it appeared earlier (so each value is printed once), otherwise count its later occurrences. Two nested passes make it O(n²) with O(1) extra space.")
    yield snippet("py", '''
        def count_freq(arr):
            n = len(arr)
            for i in range(n):
                if any(arr[j] == arr[i] for j in range(i)):   # already counted
                    continue
                count = 1
                for j in range(i + 1, n):
                    if arr[j] == arr[i]:
                        count += 1
                print(arr[i], count)

        count_freq([10, 12, 10, 15, 10, 20, 12, 12])
    ''', out='''
        10 3
        12 3
        15 1
        20 1
    ''')
    yield complexity("O(n²)", "O(1)")
    yield idea("**Efficient solution** — one pass with a hash map from value to count: `freq[x] += 1` is an O(1) average update, so the whole array is processed in O(n). Hash maps iterate in an unspecified order, so the keys are sorted before printing to make the output deterministic.")
    yield multi('''
        10 3
        12 3
        15 1
        20 1
    ''', py='''
        def count_freq(arr):
            freq = {}
            for x in arr:
                freq[x] = freq.get(x, 0) + 1      # O(1) average per element
            for x in sorted(freq):                # sort only for a deterministic printout
                print(x, freq[x])

        count_freq([10, 12, 10, 15, 10, 20, 12, 12])
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <unordered_map>
        #include <algorithm>
        using namespace std;

        void countFreq(const vector<int>& arr) {
            unordered_map<int, int> freq;
            for (int x : arr) freq[x]++;          // O(1) average per element
            vector<int> keys;
            for (auto& kv : freq) keys.push_back(kv.first);
            sort(keys.begin(), keys.end());       // sort only for a deterministic printout
            for (int k : keys) cout << k << " " << freq[k] << "\\n";
        }

        int main() {
            countFreq({10, 12, 10, 15, 10, 20, 12, 12});
        }
    ''', java='''
        import java.util.HashMap;
        import java.util.Map;
        import java.util.TreeSet;

        public class Main {
            static void countFreq(int[] arr) {
                Map<Integer, Integer> freq = new HashMap<>();
                for (int x : arr) freq.merge(x, 1, Integer::sum);   // O(1) average per element
                for (int k : new TreeSet<>(freq.keySet()))          // sort only for a deterministic printout
                    System.out.println(k + " " + freq.get(k));
            }

            public static void main(String[] args) {
                countFreq(new int[]{10, 12, 10, 15, 10, 20, 12, 12});
            }
        }
    ''', js='''
        function countFreq(arr) {
            const freq = new Map();
            for (const x of arr) freq.set(x, (freq.get(x) ?? 0) + 1);   // O(1) average per element
            const keys = [...freq.keys()].sort((a, b) => a - b);        // sort only for a deterministic printout
            for (const k of keys) console.log(k, freq.get(k));
        }

        countFreq([10, 12, 10, 15, 10, 20, 12, 12]);
    ''')
    yield complexity("O(n) average (O(n log n) with the final sort)", "O(n)")
    yield note("If the output must follow **first appearance** order instead, Python `dict` and JavaScript `Map` already preserve insertion order; use `LinkedHashMap` in Java and keep a separate `vector` of first-seen keys in C++.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why is a hash table O(1) only on average?",
             "The hash function could map every key to the same slot; then every operation walks a chain (or probe sequence) of length `n`. With a uniform hash function and bounded load factor the *expected* chain length is `α`, a constant, giving O(1) expected time. Balanced BSTs guarantee O(log n) in the worst case, which is why they are preferred when adversarial inputs or hard latency bounds matter.")
    yield qa("What is the load factor and what happens when it gets too high?",
             "`α = n / m`, keys per slot. Chaining cost grows linearly as `1 + α`; open addressing grows as `1 / (1 - α)` and explodes near 1. Libraries rehash into a table about twice as big when `α` crosses a threshold (0.75 in Java's `HashMap`), re-inserting all keys — O(n) once, amortised O(1) per insert.")
    yield qa("Why can't you just empty a slot when deleting from an open-addressing table?",
             "Searches stop at the first empty slot. Keys that were inserted *past* the deleted slot (because it was occupied at the time) would no longer be reachable. A DELETED tombstone keeps searches going while letting inserts reuse the slot. Too many tombstones slow down searches, so tables rehash when live + deleted slots get numerous.")
    yield qa("Chaining or open addressing — which would you choose?",
             "Chaining when deletions are frequent, the load is unpredictable or the hash function is mediocre: it never fills and degrades gracefully. Open addressing when memory locality matters and keys are small (ints): it avoids pointer chasing and allocation, which is why high-performance tables (Google's SwissTable, Python's `dict`) use open addressing with careful probing.")
    yield qa("Why should the table size be prime for modulo hashing?",
             "`key % m` with `m = 2^k` keeps only the low `k` bits of the key, so keys differing only in higher bits collide. Keys that are multiples of a common factor of `m` land in a fraction of the slots. A prime `m` shares no factors with typical key patterns and spreads them over all slots.")


@topic(G, "set", "Set", "circles")
def _():
    yield lead("A set stores **distinct** elements with no order and no index, and answers *is `x` present?* in O(1) on average. It is a hash table that stores keys only — the right structure for de-duplication, membership tests and set algebra.")
    yield define("Hash set", "a collection of unique elements implemented with a hash table. Each element is hashed to a slot; adding an existing element does nothing, so duplicates can never appear. Python `set`, C++ `unordered_set`, Java `HashSet`, JavaScript `Set`.")
    yield diagram('''
        add(10), add(20), add(30), add(20)  with  h(x) = x % 4

        slot 0 │ 20 │       ← the second add(20) finds 20 already here and does nothing
        slot 1 │    │
        slot 2 │ 10 │──▶│ 30 │
        slot 3 │    │

        size = 3, iteration order follows the slots, not the insertion order
    ''', "A hash set is a hash table whose slots hold just the keys")

    yield section("Properties of a set", "list-check")
    yield cards(
        ("Distinct elements", "Adding an element that is already present is a no-op. `{1, 1, 2}` has size 2.", "circles"),
        ("Unordered", "Elements are stored by hash slot; iteration order is not insertion order and may change after a rehash.", "arrows-shuffle"),
        ("No indexing", "There is no `s[0]` — use membership tests and iteration instead.", "hash"),
        ("Fast set algebra", "Union, intersection and difference run in time linear in the sizes of the sets.", "circles-relation"),
        ("Hashing internally", "Every operation is a hash lookup — O(1) average, O(n) worst case.", "bolt"),
        ("Hashable elements only", "Elements must be immutable / have a stable hash: numbers, strings, tuples — not Python lists or dicts.", "lock"),
        cols=3,
    )
    yield table(
        ["Operation", "Python", "Average", "Why"],
        ["add", "`s.add(x)`", "O(1)", "Hash `x`, place it in its slot if absent"],
        ["remove", "`s.remove(x)` (error if missing) / `s.discard(x)` (silent)", "O(1)", "Hash `x`, unlink it from its slot"],
        ["membership", "`x in s`", "O(1)", "Hash `x`, compare with the keys in that slot only"],
        ["size", "`len(s)`", "O(1)", "A counter maintained on add/remove"],
        ["union / intersection / difference", "`a | b`, `a & b`, `a - b`, `a ^ b`", "O(len(a) + len(b))", "Iterate one set, test membership in the other"],
        ["subset / superset / disjoint", "`a <= b`, `a >= b`, `a.isdisjoint(b)`", "O(min(len(a), len(b)))", "Test every element of the smaller set against the other"],
        ["iterate", "`for x in s`", "O(n)", "Walk every slot"],
    )

    yield section("Set containers in the four languages", "box")
    yield table(
        ["Language", "Hash set (unordered, O(1) avg)", "Ordered set (sorted, O(log n))"],
        ["Python", "`set`, immutable `frozenset`", "— (use `sorted(s)` when needed, or `bisect` on a list)"],
        ["C++", "`std::unordered_set`", "`std::set` (red-black tree)"],
        ["Java", "`HashSet`; `LinkedHashSet` keeps insertion order", "`TreeSet` (red-black tree)"],
        ["JavaScript", "`Set` (keeps insertion order by specification)", "— (sort an array)"],
    )
    yield note("Choose the **hash** version by default. Switch to the **ordered** version only when you need sorted iteration, `min`/`max`, floor/ceiling or range queries — those cost O(log n) per operation instead of O(1).")

    yield section("Creating a set and adding elements", "plus")
    yield p("A set is built from a literal or from any iterable (duplicates are dropped on the way in). Elements are added one at a time or in bulk. Because iteration order differs between languages, the programs below **sort** before printing.")
    yield multi('''
        from list with duplicates: 1 2 3 4
        size: 4
        after add 30: 10 20 30
        after bulk add: 10 20 30 40 50 60 70 80 90
        size: 9
    ''', py='''
        def show(label, s):
            print(label + ":", *sorted(s))

        s2 = set([1, 2, 3, 4, 1, 2, 3, 4])        # duplicates dropped
        show("from list with duplicates", s2)
        print("size:", len(s2))

        s = {10, 20}                                # a set literal
        s.add(30)                                   # one element
        show("after add 30", s)
        s.update([40, 50])                          # any iterable
        s.update([60, 70], {80, 90})                # several at once
        show("after bulk add", s)
        print("size:", len(s))
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        #include <algorithm>
        #include <string>
        using namespace std;

        void show(const string& label, const unordered_set<int>& s) {
            vector<int> v(s.begin(), s.end());
            sort(v.begin(), v.end());
            cout << label << ":";
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            vector<int> data = {1, 2, 3, 4, 1, 2, 3, 4};
            unordered_set<int> s2(data.begin(), data.end());   // duplicates dropped
            show("from list with duplicates", s2);
            cout << "size: " << s2.size() << "\\n";

            unordered_set<int> s = {10, 20};
            s.insert(30);                                       // one element
            show("after add 30", s);
            s.insert({40, 50});                                 // several at once
            for (int x : {60, 70, 80, 90}) s.insert(x);
            show("after bulk add", s);
            cout << "size: " << s.size() << "\\n";
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static void show(String label, Set<Integer> s) {
                StringBuilder sb = new StringBuilder(label + ":");
                for (int x : new TreeSet<>(s)) sb.append(" ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Set<Integer> s2 = new HashSet<>(List.of(1, 2, 3, 4, 1, 2, 3, 4));   // duplicates dropped
                show("from list with duplicates", s2);
                System.out.println("size: " + s2.size());

                Set<Integer> s = new HashSet<>(List.of(10, 20));
                s.add(30);                                   // one element
                show("after add 30", s);
                s.addAll(List.of(40, 50));                   // any collection
                s.addAll(List.of(60, 70, 80, 90));
                show("after bulk add", s);
                System.out.println("size: " + s.size());
            }
        }
    ''', js='''
        const show = (label, s) => console.log(label + ":", [...s].sort((a, b) => a - b).join(" "));

        const s2 = new Set([1, 2, 3, 4, 1, 2, 3, 4]);   // duplicates dropped
        show("from list with duplicates", s2);
        console.log("size:", s2.size);

        const s = new Set([10, 20]);
        s.add(30);                                      // one element
        show("after add 30", s);
        for (const x of [40, 50]) s.add(x);             // no bulk add — loop
        for (const x of [60, 70, 80, 90]) s.add(x);
        show("after bulk add", s);
        console.log("size:", s.size);
    ''')
    yield complexity("O(1) average per add", "O(n)")
    yield pitfall("In Python `s = {}` creates an empty **dict**, not a set — `type({})` is `dict`. The only way to write an empty set is `set()`. Set literals with elements (`{1, 2}`) are fine.")

    yield section("Removing elements", "trash")
    yield p("Python offers two ways to remove: `discard(x)` silently ignores a missing element, `remove(x)` raises `KeyError`. C++ `erase`, Java `remove` and JavaScript `delete` behave like `discard` and report whether anything was removed. `clear()` empties the set in every language.")
    yield multi('''
        after discard 30: 10 20
        removed 20: true
        after remove 20: 10
        removed 99: false
        after clear, size: 0
    ''', py='''
        def show(label, s):
            print(label + ":", *sorted(s))

        s = {10, 20, 30}
        s.discard(30)                               # silent if missing
        show("after discard 30", s)
        removed = 20 in s
        s.remove(20)                                # KeyError if missing
        print("removed 20:", "true" if removed else "false")
        show("after remove 20", s)
        removed = 99 in s
        s.discard(99)
        print("removed 99:", "true" if removed else "false")
        s.clear()
        print("after clear, size:", len(s))
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        #include <algorithm>
        #include <string>
        using namespace std;

        void show(const string& label, const unordered_set<int>& s) {
            vector<int> v(s.begin(), s.end());
            sort(v.begin(), v.end());
            cout << label << ":";
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            unordered_set<int> s = {10, 20, 30};
            s.erase(30);                                        // returns number erased (0 or 1)
            show("after discard 30", s);
            cout << "removed 20: " << (s.erase(20) ? "true" : "false") << "\\n";
            show("after remove 20", s);
            cout << "removed 99: " << (s.erase(99) ? "true" : "false") << "\\n";
            s.clear();
            cout << "after clear, size: " << s.size() << "\\n";
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static void show(String label, Set<Integer> s) {
                StringBuilder sb = new StringBuilder(label + ":");
                for (int x : new TreeSet<>(s)) sb.append(" ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Set<Integer> s = new HashSet<>(List.of(10, 20, 30));
                s.remove(30);                                // returns boolean, no exception
                show("after discard 30", s);
                System.out.println("removed 20: " + s.remove(20));
                show("after remove 20", s);
                System.out.println("removed 99: " + s.remove(99));
                s.clear();
                System.out.println("after clear, size: " + s.size());
            }
        }
    ''', js='''
        const show = (label, s) => console.log(label + ":", [...s].sort((a, b) => a - b).join(" "));

        const s = new Set([10, 20, 30]);
        s.delete(30);                                   // returns boolean, no exception
        show("after discard 30", s);
        console.log("removed 20:", s.delete(20));
        show("after remove 20", s);
        console.log("removed 99:", s.delete(99));
        s.clear();
        console.log("after clear, size:", s.size);
    ''')
    yield complexity("O(1) average per removal", "O(1)")

    yield section("Membership and aggregates", "search")
    yield p("`x in s` is the operation sets exist for: hash `x`, look in one slot. The aggregates `len`, `max`, `min`, `sum` are ordinary iterations — O(1) for `len` (a stored counter) and O(n) for the rest, because a hash set keeps no order.")
    yield multi('''
        size: 4
        max: 40
        min: 10
        sum: 100
        20 in s: true
        50 in s: false
    ''', py='''
        s = {10, 20, 30, 40}
        print("size:", len(s))                     # O(1)
        print("max:", max(s))                      # O(n) — a hash set is not sorted
        print("min:", min(s))
        print("sum:", sum(s))
        print("20 in s:", "true" if 20 in s else "false")   # O(1) average
        print("50 in s:", "true" if 50 in s else "false")
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        #include <algorithm>
        #include <numeric>
        using namespace std;

        int main() {
            unordered_set<int> s = {10, 20, 30, 40};
            cout << "size: " << s.size() << "\\n";                       // O(1)
            cout << "max: " << *max_element(s.begin(), s.end()) << "\\n";   // O(n) — not sorted
            cout << "min: " << *min_element(s.begin(), s.end()) << "\\n";
            cout << "sum: " << accumulate(s.begin(), s.end(), 0) << "\\n";
            cout << "20 in s: " << (s.count(20) ? "true" : "false") << "\\n";   // O(1) average
            cout << "50 in s: " << (s.contains(50) ? "true" : "false") << "\\n"; // C++20
        }
    ''', java='''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<Integer> s = new HashSet<>(List.of(10, 20, 30, 40));
                System.out.println("size: " + s.size());                      // O(1)
                System.out.println("max: " + Collections.max(s));             // O(n) — not sorted
                System.out.println("min: " + Collections.min(s));
                int sum = 0;
                for (int x : s) sum += x;
                System.out.println("sum: " + sum);
                System.out.println("20 in s: " + s.contains(20));             // O(1) average
                System.out.println("50 in s: " + s.contains(50));
            }
        }
    ''', js='''
        const s = new Set([10, 20, 30, 40]);
        console.log("size:", s.size);                       // O(1)
        console.log("max:", Math.max(...s));                // O(n) — not sorted
        console.log("min:", Math.min(...s));
        console.log("sum:", [...s].reduce((a, b) => a + b, 0));
        console.log("20 in s:", s.has(20));                 // O(1) average
        console.log("50 in s:", s.has(50));
    ''')
    yield complexity("O(1) membership, O(n) aggregates", "O(1)")
    yield good("Replace `x in some_list` (O(n) scan) by `x in some_set` (O(1)) whenever the same collection is tested many times — the single most common hashing speed-up in interview solutions.")

    yield section("Set algebra: union, intersection, difference", "circles-relation")
    yield diagram('''
        s1 = {10, 20, 30}      s2 = {30, 40, 50}

        union          s1 | s2   = {10, 20, 30, 40, 50}   everything in either
        intersection   s1 & s2   = {30}                   only what is in both
        difference     s1 - s2   = {10, 20}               in s1 but not in s2
        symmetric diff s1 ^ s2   = {10, 20, 40, 50}       in exactly one of them
    ''', "The four set operations on two sets that share one element")
    yield p("Each operation iterates one set and tests membership in the other, so it costs O(|s1| + |s2|). Python has operators and named methods (`s1.union(s2)`); C++ needs a loop (or `std::set_union` on **sorted** containers); Java uses the mutating `addAll` / `retainAll` / `removeAll` on a copy; JavaScript gained `union`, `intersection`, `difference` and `symmetricDifference` methods on `Set` in ES2025 (Node 22+).")
    yield multi('''
        union: 10 20 30 40 50
        intersection: 30
        difference: 10 20
        symmetric difference: 10 20 40 50
    ''', py='''
        def show(label, s):
            print(label + ":", *sorted(s))

        s1 = {10, 20, 30}
        s2 = {30, 40, 50}
        show("union", s1 | s2)                      # also s1.union(s2)
        show("intersection", s1 & s2)               # s1.intersection(s2)
        show("difference", s1 - s2)                 # s1.difference(s2)
        show("symmetric difference", s1 ^ s2)       # s1.symmetric_difference(s2)
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        #include <algorithm>
        #include <string>
        using namespace std;
        using Set = unordered_set<int>;

        void show(const string& label, const Set& s) {
            vector<int> v(s.begin(), s.end());
            sort(v.begin(), v.end());
            cout << label << ":";
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        Set unionOf(const Set& a, const Set& b) { Set r = a; r.insert(b.begin(), b.end()); return r; }
        Set intersection(const Set& a, const Set& b) {
            Set r;
            for (int x : a) if (b.count(x)) r.insert(x);     // in both
            return r;
        }
        Set difference(const Set& a, const Set& b) {
            Set r;
            for (int x : a) if (!b.count(x)) r.insert(x);    // in a, not in b
            return r;
        }
        Set symmetricDifference(const Set& a, const Set& b) {
            return unionOf(difference(a, b), difference(b, a));
        }

        int main() {
            Set s1 = {10, 20, 30}, s2 = {30, 40, 50};
            show("union", unionOf(s1, s2));
            show("intersection", intersection(s1, s2));
            show("difference", difference(s1, s2));
            show("symmetric difference", symmetricDifference(s1, s2));
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static void show(String label, Set<Integer> s) {
                StringBuilder sb = new StringBuilder(label + ":");
                for (int x : new TreeSet<>(s)) sb.append(" ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Set<Integer> s1 = Set.of(10, 20, 30), s2 = Set.of(30, 40, 50);

                Set<Integer> union = new HashSet<>(s1); union.addAll(s2);
                Set<Integer> inter = new HashSet<>(s1); inter.retainAll(s2);      // keep only what is in s2
                Set<Integer> diff = new HashSet<>(s1); diff.removeAll(s2);        // drop what is in s2
                Set<Integer> sym = new HashSet<>(union); sym.removeAll(inter);    // union minus intersection

                show("union", union);
                show("intersection", inter);
                show("difference", diff);
                show("symmetric difference", sym);
            }
        }
    ''', js='''
        const show = (label, s) => console.log(label + ":", [...s].sort((a, b) => a - b).join(" "));

        const s1 = new Set([10, 20, 30]);
        const s2 = new Set([30, 40, 50]);
        show("union", s1.union(s2));                            // ES2025 Set methods
        show("intersection", s1.intersection(s2));
        show("difference", s1.difference(s2));
        show("symmetric difference", s1.symmetricDifference(s2));
    ''')
    yield complexity("O(|s1| + |s2|)", "O(|s1| + |s2|)")
    yield note("The mutating forms update a set in place: Python `s1 |= s2`, `s1 &= s2`, `s1 -= s2` (or `update`, `intersection_update`, `difference_update`); Java's `addAll` / `retainAll` / `removeAll` are *only* mutating, which is why the sample copies first.")

    yield section("Subset, superset and disjoint tests", "git-compare")
    yield table(
        ["Test", "Meaning", "Python", "Cost"],
        ["`a.isdisjoint(b)`", "No common element", "`a.isdisjoint(b)`", "O(min(|a|, |b|))"],
        ["`a <= b`", "Every element of `a` is in `b` (subset, possibly equal)", "`a.issubset(b)`", "O(|a|)"],
        ["`a < b`", "Subset **and** `a != b` (proper subset)", "`a < b`", "O(|a|)"],
        ["`a >= b`", "`a` contains every element of `b` (superset)", "`a.issuperset(b)`", "O(|b|)"],
        ["`a > b`", "Proper superset", "`a > b`", "O(|b|)"],
    )
    yield multi('''
        s1 disjoint s2: true
        s2 disjoint s1: true
        s1 disjoint s1: false
        s1 <= s2: false
        s1 < s2: false
        s1 >= s2: false
        s1 > s2: false
        {10} <= s1: true
        {10} < s1: true
        s1 <= s1: true
        s1 < s1: false
    ''', py='''
        def b(x): return "true" if x else "false"

        s1 = {10, 20}
        s2 = {40, 30, 50}
        print("s1 disjoint s2:", b(s1.isdisjoint(s2)))   # no common element
        print("s2 disjoint s1:", b(s2.isdisjoint(s1)))
        print("s1 disjoint s1:", b(s1.isdisjoint(s1)))   # a non-empty set shares everything with itself
        print("s1 <= s2:", b(s1 <= s2))                   # subset
        print("s1 < s2:", b(s1 < s2))                     # proper subset
        print("s1 >= s2:", b(s1 >= s2))                   # superset
        print("s1 > s2:", b(s1 > s2))                     # proper superset
        print("{10} <= s1:", b({10} <= s1))
        print("{10} < s1:", b({10} < s1))
        print("s1 <= s1:", b(s1 <= s1))                   # a set is a subset of itself …
        print("s1 < s1:", b(s1 < s1))                     # … but not a proper one
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        using namespace std;
        using Set = unordered_set<int>;

        bool isDisjoint(const Set& a, const Set& b) {
            const Set& small = a.size() < b.size() ? a : b;
            const Set& big = a.size() < b.size() ? b : a;
            for (int x : small) if (big.count(x)) return false;
            return true;
        }
        bool isSubset(const Set& a, const Set& b) {          // a ⊆ b
            if (a.size() > b.size()) return false;
            for (int x : a) if (!b.count(x)) return false;
            return true;
        }
        bool isProperSubset(const Set& a, const Set& b) { return a.size() < b.size() && isSubset(a, b); }
        const char* B(bool x) { return x ? "true" : "false"; }

        int main() {
            Set s1 = {10, 20}, s2 = {40, 30, 50}, one = {10};
            cout << "s1 disjoint s2: " << B(isDisjoint(s1, s2)) << "\\n";
            cout << "s2 disjoint s1: " << B(isDisjoint(s2, s1)) << "\\n";
            cout << "s1 disjoint s1: " << B(isDisjoint(s1, s1)) << "\\n";
            cout << "s1 <= s2: " << B(isSubset(s1, s2)) << "\\n";
            cout << "s1 < s2: " << B(isProperSubset(s1, s2)) << "\\n";
            cout << "s1 >= s2: " << B(isSubset(s2, s1)) << "\\n";
            cout << "s1 > s2: " << B(isProperSubset(s2, s1)) << "\\n";
            cout << "{10} <= s1: " << B(isSubset(one, s1)) << "\\n";
            cout << "{10} < s1: " << B(isProperSubset(one, s1)) << "\\n";
            cout << "s1 <= s1: " << B(isSubset(s1, s1)) << "\\n";
            cout << "s1 < s1: " << B(isProperSubset(s1, s1)) << "\\n";
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static boolean isDisjoint(Set<Integer> a, Set<Integer> b) { return Collections.disjoint(a, b); }
            static boolean isSubset(Set<Integer> a, Set<Integer> b) { return b.containsAll(a); }     // a ⊆ b
            static boolean isProperSubset(Set<Integer> a, Set<Integer> b) { return a.size() < b.size() && b.containsAll(a); }

            public static void main(String[] args) {
                Set<Integer> s1 = Set.of(10, 20), s2 = Set.of(40, 30, 50), one = Set.of(10);
                System.out.println("s1 disjoint s2: " + isDisjoint(s1, s2));
                System.out.println("s2 disjoint s1: " + isDisjoint(s2, s1));
                System.out.println("s1 disjoint s1: " + isDisjoint(s1, s1));
                System.out.println("s1 <= s2: " + isSubset(s1, s2));
                System.out.println("s1 < s2: " + isProperSubset(s1, s2));
                System.out.println("s1 >= s2: " + isSubset(s2, s1));
                System.out.println("s1 > s2: " + isProperSubset(s2, s1));
                System.out.println("{10} <= s1: " + isSubset(one, s1));
                System.out.println("{10} < s1: " + isProperSubset(one, s1));
                System.out.println("s1 <= s1: " + isSubset(s1, s1));
                System.out.println("s1 < s1: " + isProperSubset(s1, s1));
            }
        }
    ''', js='''
        const s1 = new Set([10, 20]);
        const s2 = new Set([40, 30, 50]);
        const one = new Set([10]);
        const properSubset = (a, b) => a.size < b.size && a.isSubsetOf(b);

        console.log("s1 disjoint s2:", s1.isDisjointFrom(s2));     // ES2025 Set methods
        console.log("s2 disjoint s1:", s2.isDisjointFrom(s1));
        console.log("s1 disjoint s1:", s1.isDisjointFrom(s1));
        console.log("s1 <= s2:", s1.isSubsetOf(s2));
        console.log("s1 < s2:", properSubset(s1, s2));
        console.log("s1 >= s2:", s1.isSupersetOf(s2));
        console.log("s1 > s2:", properSubset(s2, s1));
        console.log("{10} <= s1:", one.isSubsetOf(s1));
        console.log("{10} < s1:", properSubset(one, s1));
        console.log("s1 <= s1:", s1.isSubsetOf(s1));
        console.log("s1 < s1:", properSubset(s1, s1));
    ''')
    yield complexity("O(min(|a|, |b|))", "O(1)")
    yield pitfall("`<` and `>` on sets are **not** a total order: for `s1 = {10, 20}` and `s2 = {30, 40, 50}` every one of `s1 < s2`, `s1 > s2` and `s1 == s2` is false. Never sort a list of sets with these operators.")

    yield section("Iteration order", "arrows-sort")
    yield warn("A hash set iterates in **slot order**, which depends on the hash values and the table size — it is not insertion order, not sorted order, and it can change after a rehash. Any program whose output depends on it is a bug waiting to happen.")
    yield table(
        ["Container", "Iteration order"],
        ["Python `set`", "Arbitrary (small ints often *look* sorted because `hash(i) == i` — do not rely on it); string hashes are randomised per process"],
        ["C++ `unordered_set`", "Arbitrary, implementation defined"],
        ["Java `HashSet`", "Arbitrary; `LinkedHashSet` = insertion order; `TreeSet` = sorted"],
        ["JavaScript `Set`", "**Insertion order**, guaranteed by the language specification"],
    )
    yield good("When the output must be reproducible, sort first (`sorted(s)`), or use an insertion-ordered container (`LinkedHashSet`, JS `Set`, Python `dict.fromkeys(items)`) when the original order is what you want.")

    yield section("Typical uses", "apps")
    yield cards(
        ("De-duplication", "`len(set(arr))` counts distinct values; `set(arr)` drops repeats in O(n) instead of O(n²).", "copy-off"),
        ("Fast lookups", "Turn a list of allowed values / visited states / seen ids into a set and test membership in O(1).", "search"),
        ("Visited markers", "BFS/DFS on graphs store visited nodes in a set — see the Graph topics.", "route"),
        ("Pair problems", "Two-sum, pair with a given difference: scan once, test whether `target - x` has been *seen*.", "arrows-shuffle"),
        ("Set algebra", "Common friends = intersection; who left = difference; symmetric difference = what changed.", "circles-relation"),
        ("Frequency counting", "Needs counts, not just presence — that is a dictionary (next topic).", "chart-bar"),
        cols=3,
    )

    yield section("Problem: count distinct elements in an array", "copy-off")
    yield io("arr = [10, 20, 20, 10, 30]", "3", "arr = [5, 5, 5]", "1")
    yield idea("Insert every element into a set; duplicates vanish automatically, so the set's size is the number of distinct values. One pass, O(1) average per insert.")
    yield multi('''
        10 20 20 10 30 → 3 distinct
        5 5 5 → 1 distinct
        1 2 3 4 → 4 distinct
    ''', py='''
        def count_distinct(arr):
            return len(set(arr))                  # duplicates collapse on insert

        for arr in ([10, 20, 20, 10, 30], [5, 5, 5], [1, 2, 3, 4]):
            print(*arr, "→", count_distinct(arr), "distinct")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <unordered_set>
        using namespace std;

        int countDistinct(const vector<int>& arr) {
            unordered_set<int> seen(arr.begin(), arr.end());   // duplicates collapse on insert
            return (int)seen.size();
        }

        int main() {
            vector<vector<int>> tests = {{10, 20, 20, 10, 30}, {5, 5, 5}, {1, 2, 3, 4}};
            for (const auto& arr : tests) {
                for (int x : arr) cout << x << " ";
                cout << "→ " << countDistinct(arr) << " distinct\\n";
            }
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static int countDistinct(int[] arr) {
                Set<Integer> seen = new HashSet<>();
                for (int x : arr) seen.add(x);              // duplicates collapse on insert
                return seen.size();
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 20, 20, 10, 30}, {5, 5, 5}, {1, 2, 3, 4}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : arr) sb.append(x).append(" ");
                    System.out.println(sb + "→ " + countDistinct(arr) + " distinct");
                }
            }
        }
    ''', js='''
        const countDistinct = (arr) => new Set(arr).size;   // duplicates collapse on insert

        for (const arr of [[10, 20, 20, 10, 30], [5, 5, 5], [1, 2, 3, 4]])
            console.log(arr.join(" "), "→", countDistinct(arr), "distinct");
    ''')
    yield complexity("O(n) average", "O(n)")

    yield section("Problem: do two arrays have a common element?", "circles-relation")
    yield io("a = [3, 8, 12, 5], b = [7, 1, 12]", "Yes (12)", "a = [1, 2], b = [3, 4]", "No")
    yield idea("Put the smaller array in a set, then scan the other array testing membership — O(n + m) instead of the O(n · m) nested loop. This is the intersection operation stopped at the first hit.")
    yield multi('''
        [3 8 12 5] and [7 1 12] → Yes (12)
        [1 2] and [3 4] → No
    ''', py='''
        def common_element(a, b):
            seen = set(a)                          # O(len(a))
            for x in b:                            # O(len(b)) membership tests
                if x in seen:
                    return x
            return None

        for a, b in (([3, 8, 12, 5], [7, 1, 12]), ([1, 2], [3, 4])):
            found = common_element(a, b)
            result = f"Yes ({found})" if found is not None else "No"
            print(f"[{' '.join(map(str, a))}] and [{' '.join(map(str, b))}] →", result)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <unordered_set>
        #include <string>
        using namespace std;

        bool commonElement(const vector<int>& a, const vector<int>& b, int& found) {
            unordered_set<int> seen(a.begin(), a.end());   // O(len(a))
            for (int x : b)                                // O(len(b)) membership tests
                if (seen.count(x)) { found = x; return true; }
            return false;
        }

        string join(const vector<int>& v) {
            string s = "[";
            for (int i = 0; i < (int)v.size(); i++) s += (i ? " " : "") + to_string(v[i]);
            return s + "]";
        }

        int main() {
            vector<pair<vector<int>, vector<int>>> tests = {{{3, 8, 12, 5}, {7, 1, 12}}, {{1, 2}, {3, 4}}};
            for (auto& [a, b] : tests) {
                int found;
                bool ok = commonElement(a, b, found);
                cout << join(a) << " and " << join(b) << " → " << (ok ? "Yes (" + to_string(found) + ")" : "No") << "\\n";
            }
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static Integer commonElement(int[] a, int[] b) {
                Set<Integer> seen = new HashSet<>();
                for (int x : a) seen.add(x);                   // O(len(a))
                for (int x : b) if (seen.contains(x)) return x; // O(len(b)) membership tests
                return null;
            }

            static String join(int[] v) {
                StringBuilder sb = new StringBuilder("[");
                for (int i = 0; i < v.length; i++) sb.append(i > 0 ? " " : "").append(v[i]);
                return sb + "]";
            }

            public static void main(String[] args) {
                int[][][] tests = {{{3, 8, 12, 5}, {7, 1, 12}}, {{1, 2}, {3, 4}}};
                for (int[][] t : tests) {
                    Integer found = commonElement(t[0], t[1]);
                    System.out.println(join(t[0]) + " and " + join(t[1]) + " → " + (found != null ? "Yes (" + found + ")" : "No"));
                }
            }
        }
    ''', js='''
        function commonElement(a, b) {
            const seen = new Set(a);                 // O(len(a))
            for (const x of b)                       // O(len(b)) membership tests
                if (seen.has(x)) return x;
            return null;
        }

        const join = (v) => "[" + v.join(" ") + "]";
        for (const [a, b] of [[[3, 8, 12, 5], [7, 1, 12]], [[1, 2], [3, 4]]]) {
            const found = commonElement(a, b);
            console.log(join(a), "and", join(b), "→", found !== null ? `Yes (${found})` : "No");
        }
    ''')
    yield complexity("O(n + m) average", "O(min(n, m))")

    yield section("Interview Q&A", "message-question")
    yield qa("How is a set different from a list / array?",
             "A set holds each value at most once, has no positions (no `s[i]`, no order), and tests membership in O(1) average via hashing. A list keeps duplicates and order, supports O(1) indexing, but membership is an O(n) scan. Use a list when order or duplicates matter, a set when you ask *is it there?* repeatedly.")
    yield qa("Why must set elements be hashable / immutable?",
             "The element's hash decides which slot it lives in. If the element could change after insertion, its hash would change and it would be in the wrong slot — lookups would miss it. Python therefore refuses `list` and `dict` elements (`TypeError: unhashable type`) and offers `tuple` and `frozenset`; Java and C++ let you insert mutable objects but *break* if you mutate them inside the set.")
    yield qa("What are the complexities of union, intersection and difference?",
             "All three iterate one set and test membership in the other: O(|a| + |b|) for union and symmetric difference, O(min(|a|, |b|)) for intersection if you iterate the smaller one, O(|a|) for `a - b`. With sorted (tree) sets the same operations are O(|a| + |b|) by merging.")
    yield qa("When would you pick a TreeSet / std::set over a hash set?",
             "When you need the elements sorted, the smallest/largest element, the nearest value above or below a given one (`ceiling`/`floor`, `lower_bound`), or a range of elements. A hash set cannot answer any of those without a full scan; a tree set does each in O(log n).")
    yield qa("How do you remove duplicates from a list while keeping the original order?",
             "A set alone loses order. Keep a `seen` set and append to a result only when the element was not yet seen — O(n). In Python `list(dict.fromkeys(items))` does the same in one line because dicts preserve insertion order; in Java use `LinkedHashSet`; JavaScript's `[...new Set(items)]` works because `Set` keeps insertion order.")


@topic(G, "dictionary", "Dictionary", "book")
def _():
    yield lead("A dictionary (hash map) stores **key → value** pairs and finds the value for any key in O(1) on average. It is the most used data structure in practice: counting, grouping, caching and indexing are all one hash lookup away.")
    yield define("Dictionary / hash map", "a collection of key–value pairs with **distinct keys**, backed by a hash table: the key is hashed to a slot and the value is stored alongside it. Python `dict`, C++ `unordered_map`, Java `HashMap`, JavaScript `Map`.")
    yield diagram('''
        d = {110: 'xyz', 101: 'abc', 105: 'pqr'}     with  h(key) = key % 4

        slot 0 │            │
        slot 1 │ 101 → abc  │──▶│ 105 → pqr │     101 % 4 = 1 and 105 % 4 = 1 collide → chained
        slot 2 │ 110 → xyz  │
        slot 3 │            │

        lookup d[105]: h(105) = 1 → walk slot 1: 101? no, 105? yes → 'pqr'
    ''', "A hash map is a hash table whose slots hold key–value pairs")

    yield section("Properties of a dictionary", "list-check")
    yield cards(
        ("Key–value pairs", "Each entry maps a key to exactly one value: `d[110] = 'xyz'`.", "book"),
        ("Distinct keys", "Assigning to an existing key **replaces** its value; there are never two entries with the same key.", "key"),
        ("Values may repeat", "Many keys can map to the same value — only keys are unique.", "copy"),
        ("Unordered (conceptually)", "Entries live in hash slots. Python 3.7+ and JavaScript additionally remember insertion order; C++ and Java do not.", "arrows-shuffle"),
        ("Hashing internally", "Every lookup hashes the key — O(1) average, O(n) worst case.", "bolt"),
        ("Hashable keys", "Keys must be immutable with a stable hash (numbers, strings, tuples). Values can be anything.", "lock"),
        cols=3,
    )
    yield table(
        ["Operation", "Python", "Average", "Why"],
        ["insert / update", "`d[k] = v`", "O(1)", "Hash `k`; store or overwrite in its slot"],
        ["lookup", "`d[k]` (KeyError if missing) / `d.get(k, default)`", "O(1)", "Hash `k`; compare keys in that one slot"],
        ["membership", "`k in d`", "O(1)", "Same lookup, returns a boolean"],
        ["delete", "`del d[k]` / `d.pop(k)`", "O(1)", "Hash `k`; unlink the entry"],
        ["size", "`len(d)`", "O(1)", "A stored counter"],
        ["iterate", "`for k, v in d.items()`", "O(n)", "Walk every slot"],
    )

    yield section("Map containers in the four languages", "box")
    yield table(
        ["Language", "Hash map (unordered, O(1) avg)", "Ordered map (sorted keys, O(log n))"],
        ["Python", "`dict` (insertion-ordered since 3.7); `collections.Counter`, `defaultdict`", "— (use `sorted(d)`; `sortedcontainers` third-party)"],
        ["C++", "`std::unordered_map`", "`std::map` (red-black tree)"],
        ["Java", "`HashMap`; `LinkedHashMap` keeps insertion order", "`TreeMap` (red-black tree)"],
        ["JavaScript", "`Map` (insertion-ordered); plain objects `{}` for string keys only", "— (sort the keys)"],
    )
    yield note("JavaScript objects `{}` convert every key to a string (`obj[1]` and `obj[\"1\"]` are the same key). Use `Map` when keys are numbers, objects or mixed types, and whenever you need `size` without `Object.keys(...).length`.")

    yield section("Creating a dictionary, adding and reading entries", "plus")
    yield p("A dictionary is created from a literal or built up one assignment at a time. Reading `d[key]` returns the value; `keys()`, `values()` and `items()` give the three views. Below, the keys are **sorted** before printing because iteration order differs between languages.")
    yield multi('''
        size: 3
        d[101] = abc
        keys: 101 105 110
        values: abc pqr xyz
        items: 101=abc 105=pqr 110=xyz
        after d[101] = 'ABC': 101=ABC 105=pqr 110=xyz
    ''', py='''
        d = {}                       # same as {110: 'xyz', 101: 'abc', 105: 'pqr'}
        d[110] = 'xyz'
        d[101] = 'abc'
        d[105] = 'pqr'
        print("size:", len(d))
        print("d[101] =", d[101])                        # O(1) lookup
        print("keys:", *sorted(d.keys()))
        print("values:", *[d[k] for k in sorted(d)])
        print("items:", *[f"{k}={d[k]}" for k in sorted(d)])
        d[101] = 'ABC'                                   # existing key → value replaced
        print("after d[101] = 'ABC':", *[f"{k}={d[k]}" for k in sorted(d)])
    ''', cpp='''
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        #include <string>
        #include <algorithm>
        using namespace std;

        vector<int> sortedKeys(const unordered_map<int, string>& d) {
            vector<int> keys;
            for (auto& kv : d) keys.push_back(kv.first);
            sort(keys.begin(), keys.end());
            return keys;
        }

        int main() {
            unordered_map<int, string> d;    // same as {{110, "xyz"}, {101, "abc"}, {105, "pqr"}}
            d[110] = "xyz";
            d[101] = "abc";
            d[105] = "pqr";
            cout << "size: " << d.size() << "\\n";
            cout << "d[101] = " << d[101] << "\\n";                 // O(1) lookup
            cout << "keys:"; for (int k : sortedKeys(d)) cout << " " << k; cout << "\\n";
            cout << "values:"; for (int k : sortedKeys(d)) cout << " " << d[k]; cout << "\\n";
            cout << "items:"; for (int k : sortedKeys(d)) cout << " " << k << "=" << d[k]; cout << "\\n";
            d[101] = "ABC";                                          // existing key → value replaced
            cout << "after d[101] = 'ABC':"; for (int k : sortedKeys(d)) cout << " " << k << "=" << d[k]; cout << "\\n";
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static String items(Map<Integer, String> d) {
                StringBuilder sb = new StringBuilder();
                for (int k : new TreeSet<>(d.keySet())) sb.append(" ").append(k).append("=").append(d.get(k));
                return sb.toString();
            }

            public static void main(String[] args) {
                Map<Integer, String> d = new HashMap<>();   // same as Map.of(110, "xyz", 101, "abc", 105, "pqr")
                d.put(110, "xyz");
                d.put(101, "abc");
                d.put(105, "pqr");
                System.out.println("size: " + d.size());
                System.out.println("d[101] = " + d.get(101));          // O(1) lookup
                TreeSet<Integer> keys = new TreeSet<>(d.keySet());
                StringBuilder ks = new StringBuilder("keys:"), vs = new StringBuilder("values:");
                for (int k : keys) { ks.append(" ").append(k); vs.append(" ").append(d.get(k)); }
                System.out.println(ks);
                System.out.println(vs);
                System.out.println("items:" + items(d));
                d.put(101, "ABC");                                      // existing key → value replaced
                System.out.println("after d[101] = 'ABC':" + items(d));
            }
        }
    ''', js='''
        const d = new Map();          // same as new Map([[110, 'xyz'], [101, 'abc'], [105, 'pqr']])
        d.set(110, 'xyz');
        d.set(101, 'abc');
        d.set(105, 'pqr');
        const sortedKeys = () => [...d.keys()].sort((a, b) => a - b);
        const items = () => sortedKeys().map(k => `${k}=${d.get(k)}`).join(" ");

        console.log("size:", d.size);
        console.log("d[101] =", d.get(101));                 // O(1) lookup
        console.log("keys:", sortedKeys().join(" "));
        console.log("values:", sortedKeys().map(k => d.get(k)).join(" "));
        console.log("items:", items());
        d.set(101, 'ABC');                                    // existing key → value replaced
        console.log("after d[101] = 'ABC':", items());
    ''')
    yield complexity("O(1) average per insert / lookup", "O(n)")
    yield pitfall("In C++ `d[key]` on a **missing** key silently *inserts* a default value (empty string, 0) and returns it. Use `d.find(key)`, `d.count(key)`, `d.contains(key)` (C++20) or `d.at(key)` (throws) when you only want to read.")

    yield section("Missing keys and default values", "help-circle")
    yield p("What happens when the key is absent is where the languages differ most, and the source of most dictionary bugs:")
    yield table(
        ["Language", "Read of a missing key", "Safe read with default", "Membership"],
        ["Python", "`d[k]` raises `KeyError`", "`d.get(k, default)`; `d.setdefault(k, default)` also inserts", "`k in d`"],
        ["C++", "`d[k]` **inserts** a default and returns it; `d.at(k)` throws", "`auto it = d.find(k); it != d.end() ? it->second : default`", "`d.count(k)` / `d.contains(k)`"],
        ["Java", "`d.get(k)` returns `null`", "`d.getOrDefault(k, default)`", "`d.containsKey(k)`"],
        ["JavaScript", "`d.get(k)` returns `undefined`", "`d.get(k) ?? default`", "`d.has(k)`"],
    )
    yield multi('''
        get 101: abc
        get 999: none
        999 in d: false
        count of 'abc' with default 0 → 1
    ''', py='''
        d = {110: 'xyz', 101: 'abc', 105: 'pqr'}
        print("get 101:", d.get(101))
        print("get 999:", d.get(999, "none"))           # no KeyError
        print("999 in d:", "true" if 999 in d else "false")

        counts = {}
        counts['abc'] = counts.get('abc', 0) + 1       # the counting idiom
        print("count of 'abc' with default 0 →", counts['abc'])
    ''', cpp='''
        #include <iostream>
        #include <unordered_map>
        #include <string>
        using namespace std;

        string getOr(const unordered_map<int, string>& d, int k, const string& def) {
            auto it = d.find(k);                          // find does not insert
            return it != d.end() ? it->second : def;
        }

        int main() {
            unordered_map<int, string> d = {{110, "xyz"}, {101, "abc"}, {105, "pqr"}};
            cout << "get 101: " << getOr(d, 101, "none") << "\\n";
            cout << "get 999: " << getOr(d, 999, "none") << "\\n";
            cout << "999 in d: " << (d.contains(999) ? "true" : "false") << "\\n";

            unordered_map<string, int> counts;
            counts["abc"]++;                              // operator[] inserts 0 then increments — the counting idiom
            cout << "count of 'abc' with default 0 → " << counts["abc"] << "\\n";
        }
    ''', java='''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<Integer, String> d = new HashMap<>(Map.of(110, "xyz", 101, "abc", 105, "pqr"));
                System.out.println("get 101: " + d.get(101));
                System.out.println("get 999: " + d.getOrDefault(999, "none"));   // get(999) alone would be null
                System.out.println("999 in d: " + d.containsKey(999));

                Map<String, Integer> counts = new HashMap<>();
                counts.merge("abc", 1, Integer::sum);           // the counting idiom
                System.out.println("count of 'abc' with default 0 → " + counts.get("abc"));
            }
        }
    ''', js='''
        const d = new Map([[110, 'xyz'], [101, 'abc'], [105, 'pqr']]);
        console.log("get 101:", d.get(101));
        console.log("get 999:", d.get(999) ?? "none");        // get(999) alone would be undefined
        console.log("999 in d:", d.has(999));

        const counts = new Map();
        counts.set('abc', (counts.get('abc') ?? 0) + 1);     // the counting idiom
        console.log("count of 'abc' with default 0 →", counts.get('abc'));
    ''')
    yield complexity("O(1) average", "O(1)")
    yield note("Python's `collections.defaultdict(int)` and `Counter` build the default-value idiom into the container: `counts[x] += 1` just works. `Counter(arr).most_common(k)` is the one-liner for top-k frequency questions.")

    yield section("Removing entries", "trash")
    yield p("`pop(key)` removes an entry **and returns its value** (Python, and the same shape in Java's `remove`); `del d[key]` just removes it. Python's `popitem()` removes and returns the **last inserted** pair — handy as a stack of pairs — and has no equivalent in the other languages.")
    yield multi('''
        pop 101 → abc
        remaining: 105=pqr 110=xyz
        delete 105: true
        delete 999: false
        remaining: 110=xyz
    ''', py='''
        d = {110: 'xyz', 101: 'abc', 105: 'pqr'}
        def show(): print("remaining:", *[f"{k}={d[k]}" for k in sorted(d)])

        print("pop 101 →", d.pop(101))             # removes and returns the value
        show()
        print("delete 105:", "true" if d.pop(105, None) is not None else "false")
        print("delete 999:", "true" if d.pop(999, None) is not None else "false")   # default avoids KeyError
        show()
    ''', cpp='''
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        #include <string>
        #include <algorithm>
        using namespace std;

        unordered_map<int, string> d = {{110, "xyz"}, {101, "abc"}, {105, "pqr"}};

        void show() {
            vector<int> keys;
            for (auto& kv : d) keys.push_back(kv.first);
            sort(keys.begin(), keys.end());
            cout << "remaining:";
            for (int k : keys) cout << " " << k << "=" << d[k];
            cout << "\\n";
        }

        int main() {
            string v = d.at(101); d.erase(101);        // read, then erase — erase itself returns a count
            cout << "pop 101 → " << v << "\\n";
            show();
            cout << "delete 105: " << (d.erase(105) ? "true" : "false") << "\\n";
            cout << "delete 999: " << (d.erase(999) ? "true" : "false") << "\\n";
            show();
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static Map<Integer, String> d = new HashMap<>(Map.of(110, "xyz", 101, "abc", 105, "pqr"));

            static void show() {
                StringBuilder sb = new StringBuilder("remaining:");
                for (int k : new TreeSet<>(d.keySet())) sb.append(" ").append(k).append("=").append(d.get(k));
                System.out.println(sb);
            }

            public static void main(String[] args) {
                System.out.println("pop 101 → " + d.remove(101));      // removes and returns the value (null if absent)
                show();
                System.out.println("delete 105: " + (d.remove(105) != null));
                System.out.println("delete 999: " + (d.remove(999) != null));
                show();
            }
        }
    ''', js='''
        const d = new Map([[110, 'xyz'], [101, 'abc'], [105, 'pqr']]);
        const show = () => console.log("remaining:", [...d.keys()].sort((a, b) => a - b).map(k => `${k}=${d.get(k)}`).join(" "));

        const v = d.get(101); d.delete(101);        // read, then delete — delete returns a boolean
        console.log("pop 101 →", v);
        show();
        console.log("delete 105:", d.delete(105));
        console.log("delete 999:", d.delete(999));
        show();
    ''')
    yield complexity("O(1) average per removal", "O(1)")
    yield snippet("py", '''
        d = {110: 'xyz', 101: 'abc', 105: 'pqr'}
        print(d.popitem())      # last inserted pair, LIFO (Python 3.7+)
        print(d.popitem())
        print(d)
    ''', out='''
        (105, 'pqr')
        (101, 'abc')
        {110: 'xyz'}
    ''')

    yield section("Iteration order", "arrows-sort")
    yield warn("Conceptually a hash map has **no order**. Two of the four languages guarantee insertion order anyway, two do not — code that works in Python and breaks in Java or C++ is a classic porting bug.")
    yield table(
        ["Container", "Iteration order"],
        ["Python `dict`", "**Insertion order** (guaranteed since 3.7)"],
        ["C++ `unordered_map`", "Arbitrary; `std::map` = sorted by key"],
        ["Java `HashMap`", "Arbitrary; `LinkedHashMap` = insertion order; `TreeMap` = sorted by key"],
        ["JavaScript `Map`", "**Insertion order**; plain objects list integer-like keys first in ascending order, then string keys in insertion order"],
    )
    yield good("Need sorted output? Sort the keys explicitly (`for k in sorted(d)`) or use a tree map. Need first-seen order in C++/Java? Keep a separate vector/list of keys in insertion order or use `LinkedHashMap`.")

    yield section("Typical uses", "apps")
    yield cards(
        ("Frequency counting", "`count[x] += 1` over an array or text — then answer *most frequent*, *appears exactly once*, *anagram check*.", "chart-bar"),
        ("Lookup tables", "id → record, name → phone number, word → definition. A database index in miniature.", "book"),
        ("Memoisation / caching", "key = function arguments, value = result; dynamic programming top-down uses exactly this.", "bolt"),
        ("Grouping", "key = group label (first letter, sorted letters, remainder), value = list of members.", "category"),
        ("Pair problems", "Two-sum: for each `x`, has `target - x` been seen? Store value → index.", "arrows-shuffle"),
        ("Graphs", "Adjacency lists for sparse graphs with arbitrary vertex labels: `adj[u] = [v, …]`.", "topology-star"),
        cols=3,
    )

    yield section("Problem: word frequencies", "chart-bar")
    yield io("text = \"the cat and the hat and the bat\"", "and 2 / bat 1 / cat 1 / hat 1 / the 3")
    yield idea("Split into words and do `freq[word] += 1` for each — a hash map update is O(1) on average, so the whole text costs O(n). Print the keys in sorted order so the result does not depend on the language's iteration order.")
    yield multi('''
        and 2
        bat 1
        cat 1
        hat 1
        the 3
    ''', py='''
        def word_freq(text):
            freq = {}
            for w in text.split():
                freq[w] = freq.get(w, 0) + 1      # O(1) average
            for w in sorted(freq):
                print(w, freq[w])

        word_freq("the cat and the hat and the bat")
    ''', cpp='''
        #include <iostream>
        #include <sstream>
        #include <string>
        #include <unordered_map>
        #include <vector>
        #include <algorithm>
        using namespace std;

        void wordFreq(const string& text) {
            unordered_map<string, int> freq;
            istringstream in(text);
            string w;
            while (in >> w) freq[w]++;            // O(1) average
            vector<string> words;
            for (auto& kv : freq) words.push_back(kv.first);
            sort(words.begin(), words.end());
            for (const string& x : words) cout << x << " " << freq[x] << "\\n";
        }

        int main() {
            wordFreq("the cat and the hat and the bat");
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static void wordFreq(String text) {
                Map<String, Integer> freq = new HashMap<>();
                for (String w : text.split(" ")) freq.merge(w, 1, Integer::sum);   // O(1) average
                for (String w : new TreeSet<>(freq.keySet()))
                    System.out.println(w + " " + freq.get(w));
            }

            public static void main(String[] args) {
                wordFreq("the cat and the hat and the bat");
            }
        }
    ''', js='''
        function wordFreq(text) {
            const freq = new Map();
            for (const w of text.split(" ")) freq.set(w, (freq.get(w) ?? 0) + 1);   // O(1) average
            for (const w of [...freq.keys()].sort()) console.log(w, freq.get(w));
        }

        wordFreq("the cat and the hat and the bat");
    ''')
    yield complexity("O(n) average (+ O(k log k) to sort k distinct words)", "O(k)")

    yield section("Problem: two sum with a hash map", "arrows-shuffle")
    yield io("arr = [8, 3, 5, 11, 2], target = 13", "8 + 5 = 13", "arr = [1, 2, 3], target = 10", "no pair")
    yield idea("Scan once. For each `x`, the partner we need is `target - x`; if it has already been **seen**, we are done, otherwise record `x`. One hash lookup per element replaces the inner loop of the O(n²) brute force.")
    yield steps(
        ("Create an empty map", "`seen` maps a value to its index (a set suffices if indices are not needed)."),
        ("For each element `x`", "Compute `need = target - x`."),
        ("Check the map", "If `need` is in `seen`, report the pair `(need, x)`."),
        ("Record", "Otherwise store `seen[x] = index` and continue."),
    )
    yield multi('''
        [8 3 5 11 2] target 13 → 8 + 5 = 13 (indices 0, 2)
        [1 2 3] target 10 → no pair
    ''', py='''
        def two_sum(arr, target):
            seen = {}                               # value → index
            for i, x in enumerate(arr):
                need = target - x
                if need in seen:                    # O(1) instead of an inner loop
                    return seen[need], i
                seen[x] = i
            return None

        for arr, target in (([8, 3, 5, 11, 2], 13), ([1, 2, 3], 10)):
            res = two_sum(arr, target)
            label = f"[{' '.join(map(str, arr))}] target {target} →"
            if res is None:
                print(label, "no pair")
            else:
                i, j = res
                print(label, f"{arr[i]} + {arr[j]} = {target} (indices {i}, {j})")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <unordered_map>
        #include <string>
        using namespace std;

        bool twoSum(const vector<int>& arr, int target, int& i, int& j) {
            unordered_map<int, int> seen;           // value → index
            int n = arr.size();
            for (int k = 0; k < n; k++) {
                int need = target - arr[k];
                auto it = seen.find(need);          // O(1) instead of an inner loop
                if (it != seen.end()) { i = it->second; j = k; return true; }
                seen[arr[k]] = k;
            }
            return false;
        }

        int main() {
            vector<pair<vector<int>, int>> tests = {{{8, 3, 5, 11, 2}, 13}, {{1, 2, 3}, 10}};
            for (auto& [arr, target] : tests) {
                cout << "[";
                for (int k = 0; k < (int)arr.size(); k++) cout << (k ? " " : "") << arr[k];
                cout << "] target " << target << " → ";
                int i, j;
                if (twoSum(arr, target, i, j))
                    cout << arr[i] << " + " << arr[j] << " = " << target << " (indices " << i << ", " << j << ")\\n";
                else
                    cout << "no pair\\n";
            }
        }
    ''', java='''
        import java.util.*;

        public class Main {
            static int[] twoSum(int[] arr, int target) {
                Map<Integer, Integer> seen = new HashMap<>();   // value → index
                for (int k = 0; k < arr.length; k++) {
                    int need = target - arr[k];
                    if (seen.containsKey(need))                 // O(1) instead of an inner loop
                        return new int[]{seen.get(need), k};
                    seen.put(arr[k], k);
                }
                return null;
            }

            public static void main(String[] args) {
                int[][] arrays = {{8, 3, 5, 11, 2}, {1, 2, 3}};
                int[] targets = {13, 10};
                for (int t = 0; t < arrays.length; t++) {
                    int[] arr = arrays[t];
                    StringBuilder sb = new StringBuilder("[");
                    for (int k = 0; k < arr.length; k++) sb.append(k > 0 ? " " : "").append(arr[k]);
                    sb.append("] target ").append(targets[t]).append(" → ");
                    int[] res = twoSum(arr, targets[t]);
                    if (res == null) sb.append("no pair");
                    else sb.append(arr[res[0]]).append(" + ").append(arr[res[1]]).append(" = ").append(targets[t])
                           .append(" (indices ").append(res[0]).append(", ").append(res[1]).append(")");
                    System.out.println(sb);
                }
            }
        }
    ''', js='''
        function twoSum(arr, target) {
            const seen = new Map();                   // value → index
            for (let k = 0; k < arr.length; k++) {
                const need = target - arr[k];
                if (seen.has(need)) return [seen.get(need), k];   // O(1) instead of an inner loop
                seen.set(arr[k], k);
            }
            return null;
        }

        for (const [arr, target] of [[[8, 3, 5, 11, 2], 13], [[1, 2, 3], 10]]) {
            const label = `[${arr.join(" ")}] target ${target} →`;
            const res = twoSum(arr, target);
            if (res === null) console.log(label, "no pair");
            else console.log(label, `${arr[res[0]]} + ${arr[res[1]]} = ${target} (indices ${res[0]}, ${res[1]})`);
        }
    ''')
    yield complexity("O(n) average", "O(n)")
    yield pitfall("Insert `x` into the map **after** checking for its partner, not before — otherwise `target = 2x` would match an element with itself (`[5]`, target 10 → \"5 + 5\").")

    yield section("Interview Q&A", "message-question")
    yield qa("How does a dictionary achieve O(1) lookup?",
             "The key is hashed to an array index; the value sits in that slot (or in a short chain / probe sequence starting there). No scanning, no comparisons with unrelated keys. The cost is O(1) *average*: a bad hash function or an overfull table lengthens chains, and rehashing keeps the load factor bounded.")
    yield qa("Dictionary vs set — when do you need which?",
             "Both are hash tables with distinct keys. A set answers *is `x` present?*; a dictionary additionally attaches a value to each key — a count, an index, a list of members. If you catch yourself using a dictionary with all values `True`, you want a set.")
    yield qa("What can be a dictionary key?",
             "Anything hashable and immutable in Python: numbers, strings, tuples of hashables, `frozenset` — not lists, dicts or sets. Java and C++ require a consistent `hashCode`/`equals` pair (or `std::hash` plus `==`) and the object must not change while it is a key. JavaScript `Map` accepts any value including objects (compared by identity), whereas plain objects stringify every key.")
    yield qa("What is the difference between `HashMap`, `LinkedHashMap` and `TreeMap` (or `dict` vs `std::map`)?",
             "`HashMap`/`unordered_map`/`dict`: hash table, O(1) average, no ordering guarantee (Python `dict` and JS `Map` keep insertion order). `LinkedHashMap`: hash table plus a linked list through the entries — insertion order at the same O(1). `TreeMap`/`std::map`: red-black tree, keys sorted, O(log n) per operation, supports floor/ceiling/range queries. Pick by whether you need order.")
    yield qa("How would you find the first non-repeating character in a string?",
             "Two passes with a dictionary: count every character (O(n)), then scan the string again and return the first character whose count is 1. The second pass uses the *string's* order, so the hash map's iteration order never matters.")
