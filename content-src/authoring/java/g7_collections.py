from kit import *

G = "Collections Framework"


@topic(G, "collections-overview", "Collections Framework Overview", "stack-2")
def _():
    yield lead("A unified set of interfaces (`List`, `Set`, `Queue`, `Map`) and ready-made implementations — pick the interface for the *behaviour* you need, then the class for the *performance* you need.")
    yield define("Java Collections Framework (JCF)", "the `java.util` interfaces, implementations and algorithms for storing groups of objects. Collections hold **references to objects** only — primitives are autoboxed (`List<Integer>`, never `List<int>`).")
    yield section("The hierarchy", "hierarchy")
    yield flow("`Iterable<T>`", "`Collection<E>`", "`List` / `Set` / `Queue`")
    yield ul(
        "`Iterable` — anything usable in a for-each loop (`iterator()`, `forEach`).",
        "`Collection` — `add`, `remove`, `contains`, `size`, `isEmpty`, `stream()`, `removeIf`.",
        "`List` — ordered, index-based, duplicates allowed: `ArrayList`, `LinkedList`, (`Vector`, `Stack` — legacy).",
        "`Set` — no duplicates: `HashSet`, `LinkedHashSet`, `TreeSet` (`SortedSet` → `NavigableSet`).",
        "`Queue` / `Deque` — ends-oriented: `ArrayDeque`, `LinkedList`, `PriorityQueue`.",
        "`Map<K, V>` — key → value pairs. **Not** a `Collection`: `HashMap`, `LinkedHashMap`, `TreeMap`, (`Hashtable` — legacy).",
    )
    yield note("`Map` does not extend `Collection` — a map is a set of *entries*, not of elements. You view it as collections through `keySet()`, `values()` and `entrySet()`.")
    yield section("Choosing a collection", "list-check")
    yield table(
        ["Need", "Use", "Why"],
        ["Ordered list, fast random access", "`ArrayList`", "Array-backed, O(1) `get(i)`, cache-friendly"],
        ["Stack or queue", "`ArrayDeque`", "O(1) at both ends, faster than `Stack` / `LinkedList`"],
        ["Unique elements, no order", "`HashSet`", "O(1) average `add`/`contains`"],
        ["Unique, insertion order", "`LinkedHashSet`", "Hash lookup + linked list of entries"],
        ["Unique, sorted / range queries", "`TreeSet`", "Red-black tree, O(log n), `floor`/`ceiling`"],
        ["Key → value lookup", "`HashMap`", "O(1) average"],
        ["Keys in insertion / access order, LRU", "`LinkedHashMap`", "Predictable iteration, `removeEldestEntry`"],
        ["Sorted keys, nearest-key queries", "`TreeMap`", "O(log n), `floorKey`, `subMap`"],
        ["Always get the min / max next", "`PriorityQueue`", "Binary heap: O(log n) `offer`/`poll`, O(1) `peek`"],
        ["Thread-safe map", "`ConcurrentHashMap`", "Fine-grained locking, no `null`s"],
    )
    yield section("Program to the interface", "plug")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> names = new ArrayList<>();   // declare the interface type
                names.add("Asha");
                names.add("Ravi");
                names.add("Asha");                        // duplicates are fine in a List
                System.out.println(names + " size=" + names.size());

                Set<String> unique = new TreeSet<>(names); // copy constructor: every collection has one
                System.out.println(unique);

                Map<String, Integer> ages = new HashMap<>();
                ages.put("Asha", 30);
                ages.put("Asha", 31);                      // same key: value replaced
                System.out.println(ages);
            }
        }
    ''', out='''
        [Asha, Ravi, Asha] size=3
        [Asha, Ravi]
        {Asha=31}
    ''')
    yield p("Declaring `List<String> names` (not `ArrayList<String>`) lets you swap the implementation later without touching the callers.")
    yield section("Immutable factories: `List.of`, `Set.of`, `Map.of` (Java 9+)", "lock")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = List.of(3, 1, 2);
                Map<String, Integer> m = Map.of("a", 1);
                System.out.println(nums + " " + m);
                try {
                    nums.add(4);
                } catch (UnsupportedOperationException e) {
                    System.out.println("add -> UnsupportedOperationException");
                }
                try {
                    List.of("x", null);
                } catch (NullPointerException e) {
                    System.out.println("null element -> NullPointerException");
                }
                try {
                    Set.of(1, 1);
                } catch (IllegalArgumentException e) {
                    System.out.println("duplicate -> " + e.getMessage());
                }
                List<Integer> copy = List.copyOf(new ArrayList<>(nums)); // immutable snapshot
                System.out.println(copy);
            }
        }
    ''', out='''
        [3, 1, 2] {a=1}
        add -> UnsupportedOperationException
        null element -> NullPointerException
        duplicate -> duplicate element: 1
        [3, 1, 2]
    ''')
    yield table(
        ["", "`List.of(...)`", "`Arrays.asList(...)`", "`Collections.unmodifiableList(l)`"],
        ["Add / remove", "Throws", "Throws (fixed size)", "Throws"],
        ["`set(i, x)`", "Throws", "**Allowed** (writes through to the array)", "Throws"],
        ["`null` elements", "Rejected", "Allowed", "Allowed"],
        ["Sees later changes to the source?", "No source", "Yes (backed by the array)", "**Yes** — it is only a read-only *view*"],
    )
    yield warn("`Set.of` and `Map.of` have a deliberately *randomised* iteration order that can change between JVM runs — never rely on it. `Map.of` accepts up to 10 pairs; use `Map.ofEntries(Map.entry(k, v), …)` for more.")
    yield section("Legacy classes", "archive")
    yield table(
        ["Legacy", "Problem", "Modern replacement"],
        ["`Vector`", "Every method `synchronized` — slow even single-threaded", "`ArrayList` (or `CopyOnWriteArrayList`)"],
        ["`Stack`", "Extends `Vector`; exposes `get(i)`, `insertElementAt`", "`ArrayDeque` (`push`/`pop`/`peek`)"],
        ["`Hashtable`", "Global lock, no `null` keys/values", "`HashMap` / `ConcurrentHashMap`"],
        ["`Enumeration`", "No `remove`, clunky names", "`Iterator`"],
    )
    yield qa("Why doesn't Map extend Collection?",
             "A `Collection` is a group of single elements with `add(E)`. A map stores *pairs* and its core operation is `put(K, V)`; forcing it into `Collection` would give methods with no sensible meaning. Instead a map exposes three collection *views*: `keySet()`, `values()`, `entrySet()`.")
    yield qa("Collection vs Collections?",
             "`Collection` is the root **interface** of lists, sets and queues. `Collections` is a **utility class** of static helpers — `sort`, `reverse`, `unmodifiableList`, `synchronizedMap`, `emptyList`… (Similarly `Array` vs `Arrays`.)")
    yield qa("Why can't a collection hold int?",
             "Generics work only with reference types (type erasure turns `T` into `Object`). Primitives are autoboxed to `Integer` etc. — which costs memory and time. For huge numeric data use arrays or `IntStream`.")


@topic(G, "list-arraylist-linkedlist", "List: ArrayList vs LinkedList", "list-numbers")
def _():
    yield lead("`ArrayList` is a resizable array and is the right default ~99% of the time; `LinkedList` is a doubly-linked list that only wins when you add/remove at an iterator's position.")
    yield define("List", "an ordered collection with positional access (`get(i)`, `set(i, x)`, `add(i, x)`, `remove(i)`), `indexOf`, and duplicates allowed.")
    yield section("How `ArrayList` grows", "arrows-maximize")
    yield ul(
        "Backed by an `Object[] elementData`; `size` counts the slots actually used.",
        "`new ArrayList<>()` starts with an *empty* shared array; the first `add` allocates capacity **10**.",
        "When full, it grows to `old + old/2` (**1.5×**) and copies with `Arrays.copyOf` — O(n) once, so `add` is **amortised O(1)**.",
        "Pre-size with `new ArrayList<>(expected)` or `ensureCapacity(n)` to avoid repeated copying; `trimToSize()` releases the slack.",
    )
    yield formula("capacity: 10 → 15 → 22 → 33 → 49 → 73 → …")
    yield section("Complexity", "clock")
    yield table(
        ["Operation", "`ArrayList`", "`LinkedList`"],
        ["`get(i)` / `set(i, x)`", "**O(1)**", "O(n) — walks from the nearer end"],
        ["`add(x)` at the end", "O(1) amortised", "O(1)"],
        ["`add(0, x)` / `remove(0)`", "O(n) — shifts elements", "**O(1)**"],
        ["Insert/remove in the middle", "O(n) shift", "O(n) to *find* + O(1) to link"],
        ["`contains` / `indexOf`", "O(n)", "O(n)"],
        ["Memory per element", "one reference (4–8 bytes)", "node object: item + prev + next + header (~24–40 bytes)"],
        ["CPU cache", "Contiguous — very fast to scan", "Pointer chasing — slow"],
    )
    yield note("Even the “LinkedList wins at insert-in-the-middle” case usually loses in practice: finding the position is O(n) pointer-chasing, while `ArrayList` shifts with a single fast `System.arraycopy`. For a queue or stack use `ArrayDeque`, not `LinkedList`.")
    yield section("Everyday operations", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> list = new ArrayList<>(List.of("b", "c"));
                list.add(0, "a");               // insert at index
                list.add("d");
                list.set(3, "D");               // replace
                System.out.println(list + " get(1)=" + list.get(1));
                System.out.println(list.indexOf("c") + " " + list.contains("z"));
                list.remove("a");               // by value
                System.out.println(list);

                LinkedList<Integer> linked = new LinkedList<>(List.of(2, 3));
                linked.addFirst(1);
                linked.addLast(4);
                System.out.println(linked + " first=" + linked.getFirst() + " last=" + linked.peekLast());
            }
        }
    ''', out='''
        [a, b, c, D] get(1)=b
        2 false
        [b, c, D]
        [1, 2, 3, 4] first=1 last=4
    ''')
    yield section("Trap: `remove(int)` vs `remove(Object)`", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = new ArrayList<>(List.of(10, 20, 30, 1));
                nums.remove(1);                     // remove(int index) — removes 20!
                System.out.println(nums);
                nums.remove(Integer.valueOf(1));    // remove(Object) — removes the value 1
                System.out.println(nums);
            }
        }
    ''', out='''
        [10, 30, 1]
        [10, 30]
    ''')
    yield warn("With a `List<Integer>`, `remove(1)` picks the *more specific* overload `remove(int index)` — no boxing needed — so it deletes by position. Pass `Integer.valueOf(x)` (or `(Integer) x`) to delete by value.")
    yield section("`subList` is a view", "eye")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> list = new ArrayList<>(List.of(0, 1, 2, 3, 4, 5));
                List<Integer> mid = list.subList(1, 4);   // [1, 4) — a live window
                mid.set(0, 99);
                System.out.println(list);
                list.subList(0, 2).clear();               // idiom: delete a range
                System.out.println(list);
                try {
                    System.out.println(mid);              // parent was structurally modified
                } catch (ConcurrentModificationException e) {
                    System.out.println("stale subList -> ConcurrentModificationException");
                }
            }
        }
    ''', out='''
        [0, 99, 2, 3, 4, 5]
        [2, 3, 4, 5]
        stale subList -> ConcurrentModificationException
    ''')
    yield warn("A `subList` writes through to its parent and becomes invalid once the parent is structurally changed through any other path. Copy it (`new ArrayList<>(list.subList(a, b))`) if you need to keep it.")
    yield qa("ArrayList vs LinkedList — when would you pick LinkedList?",
             "Almost never. Only when you do many insertions/removals *at an iterator's current position* (`ListIterator.add/remove`) on a long list, or need the `Deque` methods on a list. Random access is O(n), and each node costs ~3–5× the memory. `ArrayDeque` beats it as a queue.")
    yield qa("What is the default capacity of ArrayList and how does it grow?",
             "Capacity 10 allocated lazily on the first `add` (the no-arg constructor starts with an empty array). When full it grows by 50% (`newCapacity = old + (old >> 1)`) and copies the array, giving amortised O(1) appends.")
    yield qa("ArrayList vs Vector?",
             "Both are resizable arrays. `Vector` synchronises every method (slow, and still not safe for compound actions like check-then-add) and doubles its size when growing; `ArrayList` is unsynchronised and grows by 1.5×. Use `ArrayList`, or `CopyOnWriteArrayList` / `Collections.synchronizedList` for threads.")


@topic(G, "set-implementations", "Set: HashSet, LinkedHashSet & TreeSet", "circles")
def _():
    yield lead("A `Set` stores each element at most once. The three implementations differ only in *ordering* and *speed*: hash (no order), linked hash (insertion order), tree (sorted).")
    yield define("Set", "a collection with no duplicate elements — `add` returns `false` if an *equal* element is already present. “Equal” means `equals`/`hashCode` for hash sets and `compareTo`/`compare` == 0 for `TreeSet`.")
    yield section("Comparison", "table")
    yield table(
        ["", "`HashSet`", "`LinkedHashSet`", "`TreeSet`"],
        ["Backed by", "a `HashMap` (elements are keys)", "a `LinkedHashMap`", "a `TreeMap` (red-black tree)"],
        ["Iteration order", "Unspecified", "Insertion order", "Sorted (natural or `Comparator`)"],
        ["`add` / `remove` / `contains`", "O(1) average", "O(1) average", "O(log n)"],
        ["`null` element", "One allowed", "One allowed", "No (`NullPointerException`)"],
        ["Needs", "`equals` + `hashCode`", "`equals` + `hashCode`", "`Comparable` or a `Comparator`"],
        ["Extra API", "—", "`reversed()`, `getFirst()` (Java 21)", "`first`, `floor`, `ceiling`, `headSet`, `subSet`…"],
    )
    yield section("Same input, three orders", "arrows-sort")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> input = List.of(42, 7, 19, 7, 3, 42);
                System.out.println("HashSet       " + new HashSet<>(input));
                System.out.println("LinkedHashSet " + new LinkedHashSet<>(input));
                System.out.println("TreeSet       " + new TreeSet<>(input));

                Set<String> seen = new HashSet<>();
                System.out.println(seen.add("x") + " " + seen.add("x"));   // second add is rejected
            }
        }
    ''', out='''
        HashSet       [19, 3, 7, 42]
        LinkedHashSet [42, 7, 19, 3]
        TreeSet       [3, 7, 19, 42]
        true false
    ''')
    yield note("`HashSet`'s order above comes from the bucket index (`hash & (capacity − 1)`: 42→10, 7→7, 19→3, 3→3 with 16 buckets). It is an implementation detail that changes as the set resizes — never depend on it.")
    yield section("`TreeSet` as a `NavigableSet`", "binary-tree")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                TreeSet<Integer> ts = new TreeSet<>(List.of(10, 20, 30, 40, 50));
                System.out.println(ts.first() + " " + ts.last());
                System.out.println(ts.floor(25) + " " + ts.ceiling(25));   // <= 25, >= 25
                System.out.println(ts.lower(20) + " " + ts.higher(20));    // < 20, > 20
                System.out.println(ts.floor(5));                           // none -> null
                System.out.println(ts.headSet(30) + " " + ts.tailSet(30)); // [..30) and [30..]
                System.out.println(ts.subSet(20, true, 40, true));
                System.out.println(ts.descendingSet());
                System.out.println(ts.pollFirst() + " -> " + ts);
            }
        }
    ''', out='''
        10 50
        20 30
        10 30
        null
        [10, 20] [30, 40, 50]
        [20, 30, 40]
        [50, 40, 30, 20, 10]
        10 -> [20, 30, 40, 50]
    ''')
    yield section("Trap: forgetting `equals`/`hashCode`", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<Point> raw = new HashSet<>();
                raw.add(new Point(1, 2));
                raw.add(new Point(1, 2));
                System.out.println("class without equals/hashCode: " + raw.size());

                Set<PointRec> rec = new HashSet<>();
                rec.add(new PointRec(1, 2));
                rec.add(new PointRec(1, 2));
                System.out.println("record: " + rec.size());
            }
        }

        class Point {                        // uses Object's identity equals/hashCode
            final int x, y;
            Point(int x, int y) { this.x = x; this.y = y; }
        }

        record PointRec(int x, int y) {}     // records generate equals/hashCode from the fields
    ''', out='''
        class without equals/hashCode: 2
        record: 1
    ''')
    yield warn("`TreeSet` ignores `equals` entirely and treats `compare(a, b) == 0` as “duplicate”. A comparator that only compares by, say, length will silently drop `\"cat\"` when `\"dog\"` is already present.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<String> byLength = new TreeSet<>(Comparator.comparingInt(String::length));
                byLength.addAll(List.of("dog", "cat", "horse"));
                System.out.println(byLength);       // "cat" looked like a duplicate of "dog"
            }
        }
    ''', out="[dog, horse]")
    yield qa("How does HashSet guarantee uniqueness?",
             "It is a wrapper around a `HashMap` whose keys are the elements and whose values are one shared dummy `PRESENT` object. `add(e)` is `map.put(e, PRESENT) == null` — so uniqueness is exactly `HashMap` key uniqueness: same bucket via `hashCode`, then `equals`.")
    yield qa("HashSet vs TreeSet — which and why?",
             "`HashSet` for fast O(1) membership when order doesn't matter. `TreeSet` when you need sorted iteration or range/nearest queries (`floor`, `ceiling`, `subSet`) at O(log n), and it requires comparable elements and rejects `null`.")
    yield qa("Can you add null to a TreeSet?",
             "Not with natural ordering — `compareTo` on `null` throws `NullPointerException`. It works only with a comparator that handles nulls, e.g. `Comparator.nullsFirst(Comparator.naturalOrder())`.")


@topic(G, "hashmap-internals", "HashMap Internals", "hash")
def _():
    yield lead("An array of buckets indexed by the key's hash: O(1) average `get`/`put`, as long as `hashCode` spreads keys well and keys never change while inside.")
    yield define("HashMap", "a hash table storing `Node<K,V>` entries (`hash`, `key`, `value`, `next`) in an array `table`. Allows one `null` key and `null` values; not thread-safe; iteration order unspecified.")
    yield section("How `put(k, v)` works", "route")
    yield steps(
        ("Hash the key", "`h = key.hashCode()`, then *spread* it: `h ^ (h >>> 16)` so the high bits influence the bucket too. A `null` key always hashes to 0."),
        ("Pick the bucket", "`index = (n - 1) & hash` — `n` (the table length) is always a power of two, so this is a fast `hash % n`."),
        ("Empty bucket?", "Store a new node there."),
        ("Collision", "Walk the bucket: if a node has the same `hash` **and** (`==` or `equals`) key, replace its value and return the old one. Otherwise append a new node."),
        ("Treeify", "If one bucket reaches **8** nodes (and the table has at least **64** buckets) the list becomes a red-black tree → worst case O(log n) instead of O(n). It turns back into a list at 6."),
        ("Resize", "If `size > capacity × loadFactor` (16 × 0.75 = 12 by default), the table doubles and entries are split between index `i` and `i + oldCap`."),
    )
    yield table(
        ["Parameter", "Default", "Meaning"],
        ["Initial capacity", "16 (allocated lazily on first `put`)", "Always rounded up to a power of two"],
        ["Load factor", "0.75", "Time/space trade-off: resize when 75% full"],
        ["`TREEIFY_THRESHOLD`", "8", "Bucket list → tree (Java 8+)"],
        ["`UNTREEIFY_THRESHOLD`", "6", "Tree → list after shrinking"],
        ["`MIN_TREEIFY_CAPACITY`", "64", "Below this, resize instead of treeifying"],
    )
    yield section("Seeing the bucket index", "calculator")
    yield snippet("java", r'''
        public class Main {
            static int spread(Object key) {
                int h;
                return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
            }

            public static void main(String[] args) {
                int n = 16;
                for (Object k : new Object[]{"Aa", "BB", 17, 33, null}) {
                    int h = spread(k);
                    System.out.println(k + " hashCode=" + (k == null ? 0 : k.hashCode()) + " bucket=" + ((n - 1) & h));
                }
            }
        }
    ''', out='''
        Aa hashCode=2112 bucket=0
        BB hashCode=2112 bucket=0
        17 hashCode=17 bucket=1
        33 hashCode=33 bucket=1
        null hashCode=0 bucket=0
    ''')
    yield note("`\"Aa\"` and `\"BB\"` have the *same* `hashCode` (2112) — a classic collision. Both still live in the map: the bucket holds a chain, and `equals` tells them apart.")
    yield section("The modern Map API", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> count = new TreeMap<>();     // TreeMap only to print in sorted order
                for (String w : "to be or not to be".split(" ")) {
                    count.merge(w, 1, Integer::sum);             // insert 1, or add 1 to the old value
                }
                System.out.println(count);
                System.out.println(count.getOrDefault("xyz", 0));

                Map<String, List<String>> groups = new TreeMap<>();
                for (String w : List.of("apple", "avocado", "banana")) {
                    groups.computeIfAbsent(w.substring(0, 1), k -> new ArrayList<>()).add(w);
                }
                System.out.println(groups);

                System.out.println(count.putIfAbsent("be", 100) + " " + count.putIfAbsent("new", 100));
                count.computeIfPresent("or", (k, v) -> null);   // returning null removes the entry
                System.out.println(count);

                for (Map.Entry<String, Integer> e : count.entrySet()) {
                    if (e.getValue() > 1) System.out.print(e.getKey() + " ");
                }
                System.out.println();
            }
        }
    ''', out='''
        {be=2, not=1, or=1, to=2}
        0
        {a=[apple, avocado], b=[banana]}
        2 null
        {be=2, new=100, not=1, to=2}
        be new to
    ''')
    yield table(
        ["Method", "Does"],
        ["`getOrDefault(k, d)`", "Value, or `d` if absent"],
        ["`putIfAbsent(k, v)`", "Put only if absent; returns the existing value (or `null`)"],
        ["`computeIfAbsent(k, fn)`", "Create the value lazily — perfect for multimaps `Map<K, List<V>>`"],
        ["`computeIfPresent(k, fn)`", "Update an existing value; `null` result removes it"],
        ["`merge(k, v, fn)`", "Put `v`, or combine with the old value — counters: `merge(k, 1, Integer::sum)`"],
        ["`entrySet()`", "Iterate keys and values together — cheaper than `keySet()` + `get`"],
    )
    yield section("Trap: mutating a key", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<List<Integer>, String> map = new HashMap<>();
                List<Integer> key = new ArrayList<>(List.of(1, 2));
                map.put(key, "found");
                key.add(3);                                  // hashCode of the key changes
                System.out.println(map.get(key));            // looks in the wrong bucket
                System.out.println(map.get(List.of(1, 2)));  // right bucket, but equals fails
                System.out.println(map.size());              // the entry is stuck in the map
            }
        }
    ''', out='''
        null
        null
        1
    ''')
    yield warn("Keys must be effectively **immutable** while they are in a `HashMap`/`HashSet`. `String`, `Integer` and records of immutable fields are ideal keys.")
    yield section("`equals` / `hashCode` contract", "scale")
    yield ul(
        "If `a.equals(b)` then `a.hashCode() == b.hashCode()` — **required**. Break it and lookups miss.",
        "Equal hash codes do *not* imply `equals` (collisions are legal, just slower).",
        "Override both or neither. `hashCode` must be stable while the object is used as a key.",
    )
    yield qa("What happens on a hash collision in HashMap?",
             "Both entries go into the same bucket: as a linked list (new node appended at the tail since Java 8), or as a red-black tree once the bucket holds 8+ nodes and capacity ≥ 64. Lookup compares `hash`, then `==`/`equals` on each node in the bucket.")
    yield qa("Why is HashMap capacity always a power of two?",
             "So the bucket index can be computed with a cheap bitmask `(n - 1) & hash` instead of `%`, and so on resize each entry either stays at index `i` or moves to `i + oldCap` (decided by one bit). The `h ^ (h >>> 16)` spreading compensates for only the low bits being used.")
    yield qa("HashMap vs Hashtable vs ConcurrentHashMap?",
             "`HashMap`: unsynchronised, one `null` key and `null` values allowed. `Hashtable`: legacy, every method synchronised on one lock, no nulls. `ConcurrentHashMap`: thread-safe with CAS + per-bin locking, lock-free reads, no nulls (so `get` returning `null` unambiguously means absent).")
    yield qa("What is the time complexity of HashMap get?",
             "O(1) average. Worst case O(n) for a bucket that is a list (all keys colliding), improved to O(log n) since Java 8 when the bucket is treeified (keys that are `Comparable` get the full benefit).")


@topic(G, "linkedhashmap-treemap", "LinkedHashMap & TreeMap", "sitemap")
def _():
    yield lead("`LinkedHashMap` = `HashMap` + a doubly-linked list for predictable order (and a two-line LRU cache). `TreeMap` = a red-black tree for sorted keys and nearest-key queries.")
    yield section("Map implementations compared", "table")
    yield table(
        ["", "`HashMap`", "`LinkedHashMap`", "`TreeMap`", "`Hashtable`"],
        ["Order", "None", "Insertion (or access)", "Sorted by key", "None"],
        ["`get` / `put`", "O(1) avg", "O(1) avg", "O(log n)", "O(1) avg"],
        ["`null` key", "One", "One", "No (natural order)", "No"],
        ["`null` values", "Yes", "Yes", "Yes", "No"],
        ["Thread-safe", "No", "No", "No", "Yes (coarse lock)"],
        ["Key requirement", "`equals`/`hashCode`", "`equals`/`hashCode`", "`Comparable`/`Comparator`", "`equals`/`hashCode`"],
        ["Use for", "Default map", "Stable order, LRU caches", "Sorted output, ranges, floor/ceiling", "Nothing new — legacy"],
    )
    yield section("`LinkedHashMap` orders", "arrows-right")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> ins = new LinkedHashMap<>();
                ins.put("banana", 2);
                ins.put("apple", 1);
                ins.put("cherry", 3);
                ins.put("banana", 20);          // re-put does NOT move the key
                System.out.println(ins);

                // accessOrder = true: every get/put moves the entry to the end
                Map<String, Integer> acc = new LinkedHashMap<>(16, 0.75f, true);
                acc.putAll(Map.of("a", 1));
                acc.put("b", 2);
                acc.put("c", 3);
                acc.get("a");
                System.out.println(acc);
            }
        }
    ''', out='''
        {banana=20, apple=1, cherry=3}
        {b=2, c=3, a=1}
    ''')
    yield section("LRU cache in a few lines", "database")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                LruCache<Integer, String> cache = new LruCache<>(2);
                cache.put(1, "one");
                cache.put(2, "two");
                cache.get(1);                 // 1 is now most recently used
                cache.put(3, "three");        // evicts 2, the least recently used
                System.out.println(cache.keySet());
            }
        }

        class LruCache<K, V> extends LinkedHashMap<K, V> {
            private final int capacity;

            LruCache(int capacity) {
                super(16, 0.75f, true);       // access order
                this.capacity = capacity;
            }

            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
                return size() > capacity;     // called after every put
            }
        }
    ''', out="[1, 3]")
    yield note("This is the standard answer to “design an LRU cache” in Java. The from-scratch version (a `HashMap` of nodes + your own doubly-linked list) has the same O(1) `get`/`put`.")
    yield section("`TreeMap` as a `NavigableMap`", "binary-tree")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                TreeMap<Integer, String> grades = new TreeMap<>();
                grades.put(90, "A");
                grades.put(80, "B");
                grades.put(70, "C");
                grades.put(0, "F");

                int score = 84;
                System.out.println(score + " -> " + grades.floorEntry(score).getValue());
                System.out.println(grades.firstKey() + " " + grades.lastKey());
                System.out.println(grades.floorKey(75) + " " + grades.ceilingKey(75));
                System.out.println(grades.ceilingEntry(95));             // no key >= 95
                System.out.println(grades.headMap(80));                  // keys < 80
                System.out.println(grades.subMap(70, true, 90, false));  // [70, 90)
                System.out.println(grades.descendingMap());
            }
        }
    ''', out='''
        84 -> B
        0 90
        70 80
        null
        {0=F, 70=C}
        {70=C, 80=B}
        {90=A, 80=B, 70=C, 0=F}
    ''')
    yield table(
        ["Method", "Returns"],
        ["`floorKey(k)` / `floorEntry(k)`", "Greatest key `<= k`"],
        ["`ceilingKey(k)` / `ceilingEntry(k)`", "Least key `>= k`"],
        ["`lowerKey(k)` / `higherKey(k)`", "Strictly `< k` / `> k`"],
        ["`firstEntry()` / `pollFirstEntry()`", "Smallest (and remove it)"],
        ["`headMap(k)` / `tailMap(k)` / `subMap(a, b)`", "Live range views"],
        ["`descendingMap()`", "Reverse-order view"],
    )
    yield warn("All the `floor`/`ceiling` methods return `null` when no such key exists — unboxing that `null` into an `int` throws `NullPointerException`.")
    yield qa("How would you implement an LRU cache in Java?",
             "Extend `LinkedHashMap` with `accessOrder = true` and override `removeEldestEntry` to return `size() > capacity`. Access order moves each touched entry to the tail; the eldest (head) is the least recently used and is evicted after a `put`. For thread safety wrap it or use a library such as Caffeine.")
    yield qa("When would you choose TreeMap over HashMap?",
             "When you need keys in sorted order or queries like “nearest key below x” (`floorKey`), “all keys in a range” (`subMap`), min/max key — e.g. time-series lookups, interval scheduling, leaderboard ranges. The cost is O(log n) per operation instead of O(1).")
    yield qa("What internal structure does TreeMap use?",
             "A red-black tree — a self-balancing binary search tree whose height stays ≤ 2·log₂(n+1), guaranteeing O(log n) `get`, `put`, `remove`. Ordering comes from `compareTo` or the supplied `Comparator`; `equals` is not used.")


@topic(G, "queue-deque", "Queue, Deque & PriorityQueue", "arrows-right-left")
def _():
    yield lead("`Queue` = FIFO line, `Deque` = double-ended (queue *and* stack), `PriorityQueue` = always hands you the smallest element next. `ArrayDeque` and `PriorityQueue` cover almost every need.")
    yield section("Two method families", "switch-horizontal")
    yield table(
        ["Action", "Throws on failure", "Returns special value"],
        ["Insert", "`add(e)` — `IllegalStateException` if full", "`offer(e)` → `false`"],
        ["Remove head", "`remove()` — `NoSuchElementException` if empty", "`poll()` → `null`"],
        ["Look at head", "`element()` — `NoSuchElementException`", "`peek()` → `null`"],
    )
    yield note("Prefer `offer`/`poll`/`peek` — empty checks become simple `null` tests. (Which is also why `ArrayDeque` and `PriorityQueue` refuse `null` elements.)")
    yield section("`ArrayDeque` as a queue and as a stack", "stack-push")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Deque<Integer> queue = new ArrayDeque<>();   // FIFO: offer at tail, poll at head
                queue.offer(1);
                queue.offer(2);
                queue.offer(3);
                System.out.println(queue.poll() + " " + queue.peek() + " " + queue);

                Deque<Integer> stack = new ArrayDeque<>();   // LIFO: push/pop at the head
                stack.push(1);
                stack.push(2);
                stack.push(3);
                System.out.println(stack.pop() + " " + stack.peek() + " " + stack);

                Deque<String> dq = new ArrayDeque<>();
                dq.offerFirst("b");
                dq.offerFirst("a");
                dq.offerLast("c");
                System.out.println(dq.pollLast() + " " + dq);
                System.out.println(new ArrayDeque<Integer>().poll());   // empty -> null
            }
        }
    ''', out='''
        1 2 [2, 3]
        3 2 [2, 1]
        c [a, b]
        null
    ''')
    yield table(
        ["Deque method", "As a queue", "As a stack"],
        ["`offerLast` / `offer`", "enqueue", "—"],
        ["`pollFirst` / `poll`", "dequeue", "—"],
        ["`push` (= `addFirst`)", "—", "push"],
        ["`pop` (= `removeFirst`)", "—", "pop"],
        ["`peekFirst` / `peek`", "front", "top"],
    )
    yield good("Use `Deque<Integer> stack = new ArrayDeque<>()` — the Javadoc of `Stack` itself recommends it. `ArrayDeque` is a circular array: O(1) amortised at both ends, no node allocation.")
    yield section("`PriorityQueue` — a binary heap", "sort-ascending")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                PriorityQueue<Integer> min = new PriorityQueue<>(List.of(5, 1, 8, 3, 2));
                System.out.println("peek=" + min.peek());
                StringBuilder sb = new StringBuilder();
                while (!min.isEmpty()) sb.append(min.poll()).append(' ');
                System.out.println("min-heap order: " + sb.toString().trim());

                PriorityQueue<Integer> max = new PriorityQueue<>(Comparator.reverseOrder());
                max.addAll(List.of(5, 1, 8, 3, 2));
                System.out.println("max first: " + max.poll() + " " + max.poll());

                PriorityQueue<String> byLen = new PriorityQueue<>(
                    Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()));
                byLen.addAll(List.of("kiwi", "fig", "banana", "date"));
                System.out.println(byLen.poll() + " " + byLen.poll() + " " + byLen.poll());
            }
        }
    ''', out='''
        peek=1
        min-heap order: 1 2 3 5 8
        max first: 8 5
        fig date kiwi
    ''')
    yield table(
        ["Operation", "Cost"],
        ["`offer` / `add`", "O(log n) — sift up"],
        ["`poll` / `remove()`", "O(log n) — sift down"],
        ["`peek`", "O(1)"],
        ["`remove(Object)` / `contains`", "O(n)"],
        ["Build from a collection", "O(n) heapify"],
    )
    yield warn("Printing or iterating a `PriorityQueue` does **not** give sorted order — only the head is guaranteed to be the minimum. Poll repeatedly to get sorted output.")
    yield section("Top-K with a size-K min-heap", "trophy")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static List<Integer> topK(int[] nums, int k) {
                PriorityQueue<Integer> heap = new PriorityQueue<>();  // min-heap of the k largest so far
                for (int x : nums) {
                    heap.offer(x);
                    if (heap.size() > k) heap.poll();                 // drop the smallest
                }
                List<Integer> res = new ArrayList<>(heap);
                res.sort(Comparator.reverseOrder());
                return res;
            }

            public static void main(String[] args) {
                System.out.println(topK(new int[]{3, 1, 9, 7, 4, 8, 2}, 3));
            }
        }
    ''', out="[9, 8, 7]")
    yield p("O(n log k) time, O(k) space — better than sorting everything (O(n log n)) when k ≪ n.")
    yield qa("Why prefer ArrayDeque over Stack and LinkedList?",
             "`Stack` extends the synchronised `Vector` (slow, and leaks list methods). `LinkedList` allocates a node per element and chases pointers. `ArrayDeque` is a resizable circular array: O(1) amortised at both ends, compact and cache-friendly. Its only restriction: no `null` elements.")
    yield qa("How do you make a max-heap in Java?",
             "`new PriorityQueue<>(Comparator.reverseOrder())`, or `(a, b) -> b - a` only when overflow is impossible — `Integer.compare(b, a)` is the safe lambda form.")
    yield qa("Is PriorityQueue thread-safe? What about blocking queues?",
             "No. Use `PriorityBlockingQueue` for a thread-safe heap. For producer–consumer, the `BlockingQueue` implementations (`ArrayBlockingQueue`, `LinkedBlockingQueue`) add `put`/`take`, which block when full/empty.")


@topic(G, "iterator-cme", "Iterators & ConcurrentModificationException", "repeat")
def _():
    yield lead("Removing from a collection while a for-each loop walks it throws `ConcurrentModificationException`. Use `removeIf`, `Iterator.remove`, or a concurrent collection.")
    yield define("Iterator", "an object with `hasNext()`, `next()` and optional `remove()` that walks a collection. The for-each loop over any `Iterable` is compiled into exactly these calls.")
    yield section("Fail-fast iterators", "alert-octagon")
    yield p("`ArrayList`, `HashMap` and friends keep a counter `modCount`, bumped on every *structural* change (add/remove, not `set`). The iterator remembers the value when it was created and checks it on each `next()`; a mismatch throws.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 4));
                try {
                    for (Integer n : nums) {
                        if (n % 2 == 0) nums.remove(n);   // structural change behind the iterator's back
                    }
                } catch (ConcurrentModificationException e) {
                    System.out.println("ConcurrentModificationException");
                }
                System.out.println(nums);
            }
        }
    ''', out='''
        ConcurrentModificationException
        [1, 3, 4]
    ''')
    yield warn("Despite the name, this has nothing to do with threads — one thread modifying a collection it is iterating is enough. It is also *best-effort*: removing the second-to-last element skips the final `hasNext()` check and silently exits without an exception, so never rely on it to catch bugs.")
    yield section("Three correct ways to remove", "check")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> a = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
                a.removeIf(n -> n % 2 == 0);                  // 1. simplest (Java 8+)
                System.out.println(a);

                List<Integer> b = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
                for (Iterator<Integer> it = b.iterator(); it.hasNext(); ) {
                    if (it.next() % 2 == 0) it.remove();      // 2. the iterator's own remove
                }
                System.out.println(b);

                List<Integer> c = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
                for (int i = c.size() - 1; i >= 0; i--) {     // 3. index loop, backwards
                    if (c.get(i) % 2 == 0) c.remove(i);
                }
                System.out.println(c);

                Map<String, Integer> m = new HashMap<>(Map.of("a", 1, "b", 2));
                m.entrySet().removeIf(e -> e.getValue() > 1); // maps: remove through a view
                System.out.println(m);
            }
        }
    ''', out='''
        [1, 3, 5]
        [1, 3, 5]
        [1, 3, 5]
        {a=1}
    ''')
    yield section("`ListIterator` — both directions, edit in place", "arrows-left-right")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> words = new ArrayList<>(List.of("a", "b", "c"));
                ListIterator<String> it = words.listIterator();
                while (it.hasNext()) {
                    int i = it.nextIndex();
                    String w = it.next();
                    if (w.equals("b")) {
                        it.set("B");          // replace the element just returned
                        it.add("b2");         // insert after it
                    }
                    System.out.print(i + ":" + w + " ");   // "c" is now at index 3
                }
                System.out.println();
                while (it.hasPrevious()) System.out.print(it.previous() + " ");
                System.out.println();
            }
        }
    ''', out='''
        0:a 1:b 3:c
        c b2 B a
    ''')
    yield section("Fail-safe (snapshot / weakly consistent) iterators", "shield")
    yield snippet("java", r'''
        import java.util.*;
        import java.util.concurrent.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> cow = new CopyOnWriteArrayList<>(List.of(1, 2, 3));
                for (Integer n : cow) {
                    if (n == 1) cow.add(99);      // iterator walks a snapshot — no exception
                    System.out.print(n + " ");
                }
                System.out.println("-> " + cow);

                Map<Integer, String> chm = new ConcurrentHashMap<>(Map.of(1, "a", 2, "b"));
                for (Integer k : chm.keySet()) chm.remove(k);   // allowed
                System.out.println(chm);
            }
        }
    ''', out='''
        1 2 3 -> [1, 2, 3, 99]
        {}
    ''')
    yield table(
        ["", "Fail-fast", "Fail-safe / weakly consistent"],
        ["Examples", "`ArrayList`, `HashMap`, `HashSet`", "`CopyOnWriteArrayList`, `ConcurrentHashMap`"],
        ["Modify while iterating", "Throws `ConcurrentModificationException`", "Allowed"],
        ["Sees changes made during iteration?", "—", "COW: never (snapshot); CHM: maybe"],
        ["Cost", "None", "COW copies the whole array on every write"],
    )
    yield qa("What causes ConcurrentModificationException and how do you avoid it?",
             "A fail-fast iterator notices `modCount` changed by something other than itself — typically `list.remove(x)` inside a for-each loop. Avoid it with `removeIf`, `Iterator.remove()`, collecting items to remove and calling `removeAll` afterwards, iterating over a copy, or using a concurrent collection.")
    yield qa("Fail-fast vs fail-safe iterators?",
             "Fail-fast iterators (most `java.util` collections) throw on concurrent structural modification. Fail-safe ones (`java.util.concurrent`) never throw: `CopyOnWriteArrayList` iterates a snapshot, `ConcurrentHashMap` is weakly consistent — it reflects some, maybe all, changes made after the iterator was created.")
    yield qa("Iterator vs ListIterator?",
             "`Iterator` works on any collection, forward only, with `remove`. `ListIterator` is for lists: moves both ways (`previous`), knows indices (`nextIndex`), and can `set` and `add` at the cursor.")


@topic(G, "comparable-comparator", "Comparable vs Comparator", "arrows-sort")
def _():
    yield lead("`Comparable` gives a class its one *natural* order (`compareTo`); a `Comparator` is any number of external orders built fluently with `comparing`, `thenComparing` and `reversed`.")
    yield table(
        ["", "`Comparable<T>`", "`Comparator<T>`"],
        ["Package", "`java.lang`", "`java.util`"],
        ["Method", "`int compareTo(T other)`", "`int compare(T a, T b)`"],
        ["Where", "Inside the class being sorted", "Separate object / lambda"],
        ["How many orders", "One — the natural order", "As many as you like"],
        ["Used by", "`Collections.sort(list)`, `TreeMap`, `Arrays.sort` with no comparator", "`list.sort(cmp)`, `new TreeSet<>(cmp)`, `stream.sorted(cmp)`"],
        ["Examples in the JDK", "`String`, `Integer`, `LocalDate`, enums", "`String.CASE_INSENSITIVE_ORDER`, `Comparator.reverseOrder()`"],
    )
    yield section("The contract", "scale")
    yield ul(
        "Return **negative** if `this < other`, **zero** if equal, **positive** if greater — only the sign matters.",
        "Antisymmetric: `sgn(a.compareTo(b)) == -sgn(b.compareTo(a))`; transitive; consistent across calls.",
        "*Strongly recommended*: consistent with `equals` (`compareTo == 0` ⇔ `equals`) — sorted sets and maps use `compareTo` for equality.",
    )
    yield section("Natural order with `Comparable`", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Version> vs = new ArrayList<>(List.of(new Version(1, 10), new Version(1, 2), new Version(0, 9)));
                Collections.sort(vs);
                System.out.println(vs);
                System.out.println(Collections.max(vs));
            }
        }

        record Version(int major, int minor) implements Comparable<Version> {
            @Override
            public int compareTo(Version o) {
                int c = Integer.compare(major, o.major);
                return c != 0 ? c : Integer.compare(minor, o.minor);
            }

            @Override
            public String toString() { return major + "." + minor; }
        }
    ''', out='''
        [0.9, 1.2, 1.10]
        1.10
    ''')
    yield section("Building comparators fluently", "stack")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            record Emp(String name, String dept, int salary) {}

            public static void main(String[] args) {
                List<Emp> staff = new ArrayList<>(List.of(
                    new Emp("Ravi", "HR", 50), new Emp("Asha", "Eng", 90),
                    new Emp("Meera", "Eng", 70), new Emp("Kiran", "HR", 50)));

                staff.sort(Comparator.comparing(Emp::dept)
                        .thenComparing(Emp::salary, Comparator.reverseOrder())
                        .thenComparing(Emp::name));
                staff.forEach(e -> System.out.println(e.dept() + " " + e.salary() + " " + e.name()));

                List<String> words = new ArrayList<>(List.of("pear", "Fig", "apple", "kiwi"));
                words.sort(Comparator.comparingInt(String::length).reversed());
                System.out.println(words);
                words.sort(String.CASE_INSENSITIVE_ORDER);
                System.out.println(words);

                List<String> withNull = new ArrayList<>(Arrays.asList("b", null, "a"));
                withNull.sort(Comparator.nullsFirst(Comparator.naturalOrder()));
                System.out.println(withNull);
            }
        }
    ''', out='''
        Eng 90 Asha
        Eng 70 Meera
        HR 50 Kiran
        HR 50 Ravi
        [apple, pear, kiwi, Fig]
        [apple, Fig, kiwi, pear]
        [null, a, b]
    ''')
    yield table(
        ["Factory / method", "Meaning"],
        ["`Comparator.comparing(keyFn)`", "Compare by an extracted `Comparable` key"],
        ["`comparingInt/Long/Double(fn)`", "Same, without boxing"],
        ["`.thenComparing(...)`", "Tie-breaker"],
        ["`.reversed()`", "Flip the whole chain built *so far*"],
        ["`Comparator.naturalOrder()` / `reverseOrder()`", "Natural order / its reverse"],
        ["`nullsFirst(cmp)` / `nullsLast(cmp)`", "Treat `null` as smallest / largest"],
    )
    yield note("Sorting is **stable** for objects (`List.sort`, `Collections.sort`, `Arrays.sort(Object[])` use TimSort): equal elements keep their relative order — which is why multi-key sorts can also be done as successive sorts.")
    yield section("Trap: comparing by subtraction", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Comparator<Integer> bad = (a, b) -> a - b;          // overflows for far-apart values
                Comparator<Integer> good = Integer::compare;
                int big = Integer.MAX_VALUE, small = -1;
                System.out.println("a - b says: " + bad.compare(big, small));
                System.out.println("compare says: " + good.compare(big, small));

                List<Integer> xs = new ArrayList<>(List.of(Integer.MIN_VALUE, 1));
                xs.sort(bad);                                       // 1 - MIN_VALUE overflows to negative
                System.out.println(xs);
            }
        }
    ''', out='''
        a - b says: -2147483648
        compare says: 1
        [1, -2147483648]
    ''')
    yield warn("`a - b` overflows when the operands have opposite signs and large magnitudes, flipping the sign and breaking the sort. Always use `Integer.compare(a, b)` or `Comparator.comparingInt`.")
    yield qa("Comparable vs Comparator — when to use which?",
             "Implement `Comparable` when the class has one obvious natural order (numbers, dates, versions). Use a `Comparator` for alternative orders, for classes you can't modify, or for multi-field sorts built with `comparing(...).thenComparing(...)`.")
    yield qa("What happens if compareTo is inconsistent with equals?",
             "Sorted collections use `compareTo` for equality, so a `TreeSet` may drop elements that `equals` considers different (or keep ones it considers equal). Classic JDK example: `new BigDecimal(\"1.0\")` and `new BigDecimal(\"1.00\")` are not `equals` (HashSet keeps 2) but compare as 0 (TreeSet keeps 1).")
    yield qa("How does reversed() behave in a chain?",
             "It reverses everything built before it. `comparing(A).thenComparing(B).reversed()` reverses both keys; to reverse only B write `thenComparing(B, Comparator.reverseOrder())` or `thenComparing(comparing(B).reversed())`.")


@topic(G, "collections-utilities", "Collections & Arrays Utilities", "tool")
def _():
    yield lead("`java.util.Collections` and `java.util.Arrays` are static toolboxes — sorting, searching, filling, copying, wrapping. Knowing them saves writing (and debugging) loops.")
    yield section("`Collections` algorithms", "list-details")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> xs = new ArrayList<>(List.of(5, 3, 9, 1, 3));
                Collections.sort(xs);
                System.out.println(xs + " binarySearch(5)=" + Collections.binarySearch(xs, 5)
                        + " binarySearch(4)=" + Collections.binarySearch(xs, 4));
                Collections.reverse(xs);
                System.out.println(xs + " max=" + Collections.max(xs) + " min=" + Collections.min(xs));
                System.out.println("frequency(3)=" + Collections.frequency(xs, 3));
                Collections.swap(xs, 0, 4);
                System.out.println(xs);
                Collections.rotate(xs, 1);
                System.out.println(xs);
                Collections.shuffle(xs, new Random(42));   // seeded -> reproducible
                System.out.println(xs);
                System.out.println(Collections.nCopies(3, "ab") + " " + String.join("", Collections.nCopies(3, "-")));
                System.out.println(Collections.disjoint(List.of(1, 2), List.of(3, 4)));
            }
        }
    ''', out='''
        [1, 3, 3, 5, 9] binarySearch(5)=3 binarySearch(4)=-4
        [9, 5, 3, 3, 1] max=9 min=1
        frequency(3)=2
        [1, 5, 3, 3, 9]
        [9, 1, 5, 3, 3]
        [1, 5, 3, 3, 9]
        [ab, ab, ab] ---
        true
    ''')
    yield note("`binarySearch` returns `-(insertionPoint) - 1` when the key is missing: `4` would be inserted at index 3, so the result is `-4`. The list must already be sorted in the same order.")
    yield section("Wrappers and empty collections", "package")
    yield table(
        ["Method", "Returns"],
        ["`Collections.unmodifiableList(l)` (…`Set`, `Map`)", "Read-only **view** — still reflects changes to `l`"],
        ["`Collections.synchronizedList(l)` (…`Map`)", "Every method locked on one mutex; iterate inside `synchronized (list) { … }`"],
        ["`Collections.emptyList()` / `emptyMap()`", "Shared immutable empty instance"],
        ["`Collections.singletonList(x)`", "Immutable one-element list"],
        ["`Collections.addAll(c, a, b, c)`", "Add varargs to any collection"],
    )
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> src = new ArrayList<>(List.of("a"));
                List<String> view = Collections.unmodifiableList(src);
                List<String> copy = List.copyOf(src);
                src.add("b");
                System.out.println(view + " " + copy);   // the view sees the change, the copy doesn't
                try {
                    view.add("c");
                } catch (UnsupportedOperationException e) {
                    System.out.println("view is read-only");
                }
            }
        }
    ''', out='''
        [a, b] [a]
        view is read-only
    ''')
    yield section("`Arrays` helpers", "brackets")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int[] a = {5, 2, 8, 1};
                Arrays.sort(a);
                System.out.println(Arrays.toString(a) + " idx(5)=" + Arrays.binarySearch(a, 5));

                int[] filled = new int[4];
                Arrays.fill(filled, -1);
                System.out.println(Arrays.toString(filled));

                int[] bigger = Arrays.copyOf(a, 6);            // pads with 0
                int[] slice = Arrays.copyOfRange(a, 1, 3);     // [1, 3)
                System.out.println(Arrays.toString(bigger) + " " + Arrays.toString(slice));

                System.out.println(Arrays.stream(a).sum() + " " + Arrays.stream(a).max().getAsInt());
                System.out.println(Arrays.equals(a, new int[]{1, 2, 5, 8}) + " " + (a == a.clone()));

                int[][] grid = {{1, 2}, {3, 4}};
                System.out.println(Arrays.deepToString(grid));

                Integer[] boxed = {3, 1, 2};
                Arrays.sort(boxed, Collections.reverseOrder()); // comparators need object arrays
                System.out.println(Arrays.toString(boxed));
            }
        }
    ''', out='''
        [1, 2, 5, 8] idx(5)=2
        [-1, -1, -1, -1]
        [1, 2, 5, 8, 0, 0] [2, 5]
        16 8
        true false
        [[1, 2], [3, 4]]
        [3, 2, 1]
    ''')
    yield note("`Arrays.sort(int[])` uses dual-pivot quicksort (not stable, but stability is meaningless for primitives); `Arrays.sort(Object[])` uses stable TimSort. Primitive arrays can't take a `Comparator` — box them or sort then reverse.")
    yield section("Trap: `Arrays.asList`", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                String[] arr = {"x", "y", "z"};
                List<String> fixed = Arrays.asList(arr);   // fixed-size view over the array
                fixed.set(0, "X");                          // allowed, writes through
                System.out.println(Arrays.toString(arr));
                try {
                    fixed.add("w");
                } catch (UnsupportedOperationException e) {
                    System.out.println("add -> UnsupportedOperationException");
                }

                int[] prim = {1, 2, 3};
                System.out.println(Arrays.asList(prim).size());      // List<int[]> with ONE element
                System.out.println(Arrays.asList(1, 2, 3).size());   // varargs of Integer

                List<String> growable = new ArrayList<>(Arrays.asList(arr));
                growable.add("w");
                System.out.println(growable);
            }
        }
    ''', out='''
        [X, y, z]
        add -> UnsupportedOperationException
        1
        3
        [X, y, z, w]
    ''')
    yield warn("`Arrays.asList` returns a fixed-size list backed by the array (no `add`/`remove`), and `Arrays.asList(intArray)` gives a `List<int[]>` of size 1. Wrap it in `new ArrayList<>(…)` for a normal list; use `Arrays.stream(ints).boxed().toList()` for primitives.")
    yield qa("What does Collections.synchronizedList not protect you from?",
             "Compound actions and iteration. Each single call is locked, but `if (!list.contains(x)) list.add(x)` can interleave between threads, and iterating requires manually holding `synchronized (list)`. Prefer `java.util.concurrent` collections.")
    yield qa("unmodifiableList vs List.copyOf vs List.of?",
             "`unmodifiableList` is a read-only *view* — changes to the backing list show through. `List.copyOf` makes an independent immutable copy (returns the argument itself if it is already an immutable list). `List.of` builds an immutable list from values. Neither of the last two allows `null`s.")
    yield qa("Which sort algorithms does Java use?",
             "`Arrays.sort` on primitives: dual-pivot quicksort, O(n log n) average, not stable. On objects and in `Collections.sort`/`List.sort`: TimSort — a stable merge/insertion hybrid, O(n log n) worst case and O(n) on already-sorted data.")
