from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Advanced Structures"


@topic(G, "trie", "Trie Data Structure", "abc")
def _():
    yield lead("A trie (prefix tree) stores a set of words as a tree of characters, so that every operation costs time proportional to the **length of the word** — not to the number of words — and so that words sharing a prefix share a path. It is the structure behind autocomplete, spell-checkers and IP routing tables.")
    yield define("Trie", "a rooted tree in which every edge is labelled with a character and every node represents the prefix spelled out by the path from the root. A flag on a node marks that this prefix is a complete word. The root represents the empty string.")
    yield diagram('''
                        (root)
                 ┌────────┼────────┐
                 b        c        g
                 │     ┌──┴──┐     │
                 a     a     u     e
               ┌─┴─┐   │     │     │
               d*  t*  t*    t*    e
                                   │
                                   k*          * = isEndOfWord
                                   │
                                   s*
    ''', "Trie for { geeks, geek, bad, bat, cat, cut } — \"geek\" and \"geeks\" share one path, \"ba\" is a prefix of two words")
    yield p("Tries are the right choice when a dictionary of words must support these operations efficiently:")
    yield ol(
        "**Search** — is this exact word in the dictionary?",
        "**Insert** — add a word.",
        "**Delete** — remove a word (without disturbing words that share its prefix).",
        "**Prefix search** — does any word start with `pre`? List them all (autocomplete).",
        "**Lexicographic ordering** — a pre-order traversal visits the words in sorted order for free.",
    )
    yield table(
        ["Operation", "Trie", "Hash table"],
        ["Search", "Θ(word_len)", "Θ(word_len) average"],
        ["Insert", "Θ(word_len)", "Θ(word_len) average"],
        ["Delete", "Θ(word_len)", "Θ(word_len) average"],
        ["Prefix search", "Θ(prefix_len)", "not supported"],
        ["Lexicographic ordering", "Θ(output_len)", "not supported (needs a sort)"],
        ["Memory", "high — up to 26 pointers per node", "low"],
    )
    yield note("A hash table matches a trie on exact-match operations, and uses far less memory. Reach for a trie only when you need **prefix** queries or **sorted** output — those are the operations a hash table simply cannot do.")

    yield section("Trie representation", "binary-tree")
    yield p("For lowercase English words each node holds an array of 26 child pointers (index `ch − 'a'`) and a boolean `isEndOfWord`. The characters themselves are not stored in the nodes — they are implied by the array index on the way down.")
    yield snippet("py", '''
        class TrieNode:
            def __init__(self):
                self.child = [None] * 26          # child[i] → node for chr(ord('a') + i), or None
                self.is_end_of_word = False       # True ⇔ the path from the root spells a stored word

        root = TrieNode()                         # the empty trie: a root with no children
        print(sum(c is not None for c in root.child), root.is_end_of_word)
    ''', out="0 False")
    yield table(
        ["Field", "Meaning"],
        ["`child[26]`", "one slot per letter; `None`/`nullptr` means no word continues with that letter"],
        ["`isEndOfWord`", "marks a complete word — needed because `geek` must be found while `gee` must not"],
    )
    yield note("Alphabets larger than 26 letters (Unicode, arbitrary bytes) use a hash map from character to child instead of a fixed array — slower per step, but the memory no longer scales with the alphabet size.", "Variants")

    yield section("Insert, search and prefix search", "search")
    yield io("insert geeks, geek, bad, bat, cat, cut; search(\"geek\")", "true", "search(\"gee\")", "false  (a prefix, not a word)", "startsWith(\"ge\")", "true")
    yield idea("All three walk the same path. **Insert** creates the missing child at every step and marks the final node. **Search** stops with `false` as soon as a child is missing and, at the end, returns the `isEndOfWord` flag. **Prefix search** is search without the final flag check.")
    yield steps(
        ("Start at the root", "with the first character of the key."),
        ("Follow child[ch − 'a']", "insert: create the node if it is missing — search: return `false` if it is missing."),
        ("At the last character", "insert: set `isEndOfWord = true` — search: return `isEndOfWord` — startsWith: return `true`."),
    )
    yield multi('''
        search geek: true
        search gee: false
        search cut: true
        search dog: false
        startsWith ge: true
        startsWith do: false
        words: bad bat cat cut geek geeks
    ''', py='''
        class TrieNode:
            def __init__(self):
                self.child = [None] * 26
                self.is_end_of_word = False

        class Trie:
            def __init__(self):
                self.root = TrieNode()

            def insert(self, key):
                node = self.root
                for ch in key:
                    i = ord(ch) - ord('a')
                    if node.child[i] is None:            # extend the path where it stops
                        node.child[i] = TrieNode()
                    node = node.child[i]
                node.is_end_of_word = True               # mark the complete word

            def _walk(self, key):                        # node where `key` ends, or None
                node = self.root
                for ch in key:
                    node = node.child[ord(ch) - ord('a')]
                    if node is None:
                        return None
                return node

            def search(self, key):
                node = self._walk(key)
                return node is not None and node.is_end_of_word

            def starts_with(self, prefix):
                return self._walk(prefix) is not None

            def words(self):                             # pre-order traversal → lexicographic order
                out = []
                def dfs(node, prefix):
                    if node.is_end_of_word:
                        out.append(prefix)
                    for i, c in enumerate(node.child):
                        if c is not None:
                            dfs(c, prefix + chr(ord('a') + i))
                dfs(self.root, "")
                return out

        trie = Trie()
        for w in ["geeks", "geek", "bad", "bat", "cat", "cut"]:
            trie.insert(w)
        for w in ["geek", "gee", "cut", "dog"]:
            print(f"search {w}:", "true" if trie.search(w) else "false")
        for pre in ["ge", "do"]:
            print(f"startsWith {pre}:", "true" if trie.starts_with(pre) else "false")
        print("words:", " ".join(trie.words()))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct TrieNode {
            TrieNode* child[26] = {};
            bool isEndOfWord = false;
        };

        class Trie {
            TrieNode* root = new TrieNode();
            TrieNode* walk(const string& key) const {           // node where `key` ends, or nullptr
                TrieNode* node = root;
                for (char ch : key) {
                    node = node->child[ch - 'a'];
                    if (!node) return nullptr;
                }
                return node;
            }
            void dfs(TrieNode* node, string& prefix, vector<string>& out) const {
                if (node->isEndOfWord) out.push_back(prefix);
                for (int i = 0; i < 26; i++)
                    if (node->child[i]) {
                        prefix.push_back('a' + i);
                        dfs(node->child[i], prefix, out);
                        prefix.pop_back();
                    }
            }
        public:
            void insert(const string& key) {
                TrieNode* node = root;
                for (char ch : key) {
                    int i = ch - 'a';
                    if (!node->child[i]) node->child[i] = new TrieNode();   // extend the path where it stops
                    node = node->child[i];
                }
                node->isEndOfWord = true;                                   // mark the complete word
            }
            bool search(const string& key) const { TrieNode* n = walk(key); return n && n->isEndOfWord; }
            bool startsWith(const string& prefix) const { return walk(prefix) != nullptr; }
            vector<string> words() const { vector<string> out; string p; dfs(root, p, out); return out; }   // sorted
        };

        int main() {
            Trie trie;
            for (string w : {"geeks", "geek", "bad", "bat", "cat", "cut"}) trie.insert(w);
            for (string w : {"geek", "gee", "cut", "dog"}) cout << "search " << w << ": " << (trie.search(w) ? "true" : "false") << "\\n";
            for (string p : {"ge", "do"}) cout << "startsWith " << p << ": " << (trie.startsWith(p) ? "true" : "false") << "\\n";
            cout << "words:";
            for (const string& w : trie.words()) cout << " " << w;
            cout << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class TrieNode {
                TrieNode[] child = new TrieNode[26];
                boolean isEndOfWord;
            }

            static class Trie {
                TrieNode root = new TrieNode();

                void insert(String key) {
                    TrieNode node = root;
                    for (char ch : key.toCharArray()) {
                        int i = ch - 'a';
                        if (node.child[i] == null) node.child[i] = new TrieNode();   // extend the path where it stops
                        node = node.child[i];
                    }
                    node.isEndOfWord = true;                                          // mark the complete word
                }
                TrieNode walk(String key) {                                           // node where key ends, or null
                    TrieNode node = root;
                    for (char ch : key.toCharArray()) {
                        node = node.child[ch - 'a'];
                        if (node == null) return null;
                    }
                    return node;
                }
                boolean search(String key) { TrieNode n = walk(key); return n != null && n.isEndOfWord; }
                boolean startsWith(String prefix) { return walk(prefix) != null; }
                List<String> words() { List<String> out = new ArrayList<>(); dfs(root, new StringBuilder(), out); return out; }
                void dfs(TrieNode node, StringBuilder prefix, List<String> out) {     // pre-order → sorted
                    if (node.isEndOfWord) out.add(prefix.toString());
                    for (int i = 0; i < 26; i++)
                        if (node.child[i] != null) {
                            prefix.append((char) ('a' + i));
                            dfs(node.child[i], prefix, out);
                            prefix.setLength(prefix.length() - 1);
                        }
                }
            }

            public static void main(String[] args) {
                Trie trie = new Trie();
                for (String w : new String[]{"geeks", "geek", "bad", "bat", "cat", "cut"}) trie.insert(w);
                for (String w : new String[]{"geek", "gee", "cut", "dog"}) System.out.println("search " + w + ": " + trie.search(w));
                for (String p : new String[]{"ge", "do"}) System.out.println("startsWith " + p + ": " + trie.startsWith(p));
                System.out.println("words: " + String.join(" ", trie.words()));
            }
        }
    ''', js='''
        class TrieNode {
            constructor() { this.child = new Array(26).fill(null); this.isEndOfWord = false; }
        }

        class Trie {
            constructor() { this.root = new TrieNode(); }
            insert(key) {
                let node = this.root;
                for (const ch of key) {
                    const i = ch.charCodeAt(0) - 97;
                    if (node.child[i] === null) node.child[i] = new TrieNode();   // extend the path where it stops
                    node = node.child[i];
                }
                node.isEndOfWord = true;                                           // mark the complete word
            }
            walk(key) {                                                            // node where key ends, or null
                let node = this.root;
                for (const ch of key) {
                    node = node.child[ch.charCodeAt(0) - 97];
                    if (node === null) return null;
                }
                return node;
            }
            search(key) { const n = this.walk(key); return n !== null && n.isEndOfWord; }
            startsWith(prefix) { return this.walk(prefix) !== null; }
            words() {                                                              // pre-order → sorted
                const out = [];
                const dfs = (node, prefix) => {
                    if (node.isEndOfWord) out.push(prefix);
                    node.child.forEach((c, i) => { if (c !== null) dfs(c, prefix + String.fromCharCode(97 + i)); });
                };
                dfs(this.root, "");
                return out;
            }
        }

        const trie = new Trie();
        for (const w of ["geeks", "geek", "bad", "bat", "cat", "cut"]) trie.insert(w);
        for (const w of ["geek", "gee", "cut", "dog"]) console.log(`search ${w}:`, trie.search(w));
        for (const p of ["ge", "do"]) console.log(`startsWith ${p}:`, trie.startsWith(p));
        console.log("words:", trie.words().join(" "));
    ''')
    yield complexity("O(L) per insert / search / startsWith for a word of length L", "O(total characters × alphabet) for the trie")
    yield pitfall("Returning `true` from `search` as soon as the walk succeeds finds `\"gee\"` even though only `\"geek\"` was inserted. The final `isEndOfWord` check is what separates *search* from *startsWith*.")

    yield section("Delete", "trash")
    yield p("Deleting must remove the word without breaking any other word that shares its path. `geeks` and `geek` share `g-e-e-k`; deleting `geeks` may remove only the `s` node, and deleting `geek` must only clear a flag.")
    yield io("insert geeks, geek, bad, bat, cat, cut; delete(\"geeks\")", "search(\"geeks\") = false, search(\"geek\") = true", "delete(\"bad\")", "search(\"bad\") = false, search(\"bat\") = true")
    yield idea("Write a recursive function that walks down to the last character. On the way **back up**: clear `isEndOfWord` at the last node; then delete a node only if it is **not** the end of another word **and** has no children. Deletion stops at the first node that is still needed.")
    yield steps(
        ("Recurse to the node of the last character", "`depth == len(key)`: unmark `isEndOfWord`."),
        ("Is this node now useless?", "No children and not the end of any word → return `null` so the parent drops its pointer."),
        ("Walk back up", "Each parent re-checks: if it is not a word end and has no children left, it is removed as well. The first node that still serves another word stops the chain."),
    )
    yield diagram('''
        delete("geeks")              delete("bad")                 delete("geek")
        g-e-e-k*-s*                  b-a-d*                        g-e-e-k*
                 └ unmark s,         a-t*                                  └ unmark k; k is a leaf → remove
                   s has no          └ unmark d; d is a leaf        e has no children now → remove
                   children →          → remove d; a still has     e → remove, g → remove
                   remove s            child t → stop              root stays (it also has b, c)
        k keeps its * — geek lives on
    ''', "The three cases: remove a leaf, stop at a shared node, remove a whole chain")
    yield multi('''
        after delete(geeks): geeks=false geek=true
        after delete(bad): bad=false bat=true
        after delete(geek): geek=false startsWith(ge)=false
        words: bat cat cut
    ''', py='''
        class TrieNode:
            def __init__(self):
                self.child = [None] * 26
                self.is_end_of_word = False

        class Trie:
            def __init__(self):
                self.root = TrieNode()

            def insert(self, key):
                node = self.root
                for ch in key:
                    i = ord(ch) - ord('a')
                    if node.child[i] is None:
                        node.child[i] = TrieNode()
                    node = node.child[i]
                node.is_end_of_word = True

            def _walk(self, key):
                node = self.root
                for ch in key:
                    node = node.child[ord(ch) - ord('a')]
                    if node is None:
                        return None
                return node

            def search(self, key):
                node = self._walk(key)
                return node is not None and node.is_end_of_word

            def starts_with(self, prefix):
                return self._walk(prefix) is not None

            def delete(self, key):
                def _delete(node, depth):                       # returns the node to keep, or None to drop it
                    if node is None:
                        return None
                    if depth == len(key):
                        node.is_end_of_word = False             # the word itself is gone …
                    else:
                        i = ord(key[depth]) - ord('a')
                        node.child[i] = _delete(node.child[i], depth + 1)
                    if node.is_end_of_word or any(c is not None for c in node.child):
                        return node                             # … but this node still serves other words
                    return None                                 # useless node: unlink it
                self.root = _delete(self.root, 0) or TrieNode()

            def words(self):
                out = []
                def dfs(node, prefix):
                    if node.is_end_of_word:
                        out.append(prefix)
                    for i, c in enumerate(node.child):
                        if c is not None:
                            dfs(c, prefix + chr(ord('a') + i))
                dfs(self.root, "")
                return out

        t = Trie()
        for w in ["geeks", "geek", "bad", "bat", "cat", "cut"]:
            t.insert(w)
        b = lambda v: "true" if v else "false"
        t.delete("geeks"); print(f"after delete(geeks): geeks={b(t.search('geeks'))} geek={b(t.search('geek'))}")
        t.delete("bad");   print(f"after delete(bad): bad={b(t.search('bad'))} bat={b(t.search('bat'))}")
        t.delete("geek");  print(f"after delete(geek): geek={b(t.search('geek'))} startsWith(ge)={b(t.starts_with('ge'))}")
        print("words:", " ".join(t.words()))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct TrieNode {
            TrieNode* child[26] = {};
            bool isEndOfWord = false;
            bool hasChild() const { for (TrieNode* c : child) if (c) return true; return false; }
        };

        class Trie {
            TrieNode* root = new TrieNode();
            TrieNode* walk(const string& key) const {
                TrieNode* node = root;
                for (char ch : key) { node = node->child[ch - 'a']; if (!node) return nullptr; }
                return node;
            }
            static TrieNode* remove(TrieNode* node, const string& key, size_t depth) {   // node to keep, or nullptr
                if (!node) return nullptr;
                if (depth == key.size()) {
                    node->isEndOfWord = false;                              // the word itself is gone …
                } else {
                    int i = key[depth] - 'a';
                    node->child[i] = remove(node->child[i], key, depth + 1);
                }
                if (node->isEndOfWord || node->hasChild()) return node;     // … but this node still serves other words
                delete node;                                                // useless node: unlink it
                return nullptr;
            }
            void dfs(TrieNode* node, string& prefix, vector<string>& out) const {
                if (node->isEndOfWord) out.push_back(prefix);
                for (int i = 0; i < 26; i++)
                    if (node->child[i]) { prefix.push_back('a' + i); dfs(node->child[i], prefix, out); prefix.pop_back(); }
            }
        public:
            void insert(const string& key) {
                TrieNode* node = root;
                for (char ch : key) {
                    int i = ch - 'a';
                    if (!node->child[i]) node->child[i] = new TrieNode();
                    node = node->child[i];
                }
                node->isEndOfWord = true;
            }
            bool search(const string& key) const { TrieNode* n = walk(key); return n && n->isEndOfWord; }
            bool startsWith(const string& p) const { return walk(p) != nullptr; }
            void erase(const string& key) { root = remove(root, key, 0); if (!root) root = new TrieNode(); }
            vector<string> words() const { vector<string> out; string p; dfs(root, p, out); return out; }
        };

        const char* b(bool v) { return v ? "true" : "false"; }

        int main() {
            Trie t;
            for (string w : {"geeks", "geek", "bad", "bat", "cat", "cut"}) t.insert(w);
            t.erase("geeks"); cout << "after delete(geeks): geeks=" << b(t.search("geeks")) << " geek=" << b(t.search("geek")) << "\\n";
            t.erase("bad");   cout << "after delete(bad): bad=" << b(t.search("bad")) << " bat=" << b(t.search("bat")) << "\\n";
            t.erase("geek");  cout << "after delete(geek): geek=" << b(t.search("geek")) << " startsWith(ge)=" << b(t.startsWith("ge")) << "\\n";
            cout << "words:";
            for (const string& w : t.words()) cout << " " << w;
            cout << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class TrieNode {
                TrieNode[] child = new TrieNode[26];
                boolean isEndOfWord;
                boolean hasChild() { for (TrieNode c : child) if (c != null) return true; return false; }
            }

            static class Trie {
                TrieNode root = new TrieNode();

                void insert(String key) {
                    TrieNode node = root;
                    for (char ch : key.toCharArray()) {
                        int i = ch - 'a';
                        if (node.child[i] == null) node.child[i] = new TrieNode();
                        node = node.child[i];
                    }
                    node.isEndOfWord = true;
                }
                TrieNode walk(String key) {
                    TrieNode node = root;
                    for (char ch : key.toCharArray()) { node = node.child[ch - 'a']; if (node == null) return null; }
                    return node;
                }
                boolean search(String key) { TrieNode n = walk(key); return n != null && n.isEndOfWord; }
                boolean startsWith(String p) { return walk(p) != null; }

                void delete(String key) { root = delete(root, key, 0); if (root == null) root = new TrieNode(); }
                TrieNode delete(TrieNode node, String key, int depth) {           // node to keep, or null to drop it
                    if (node == null) return null;
                    if (depth == key.length()) {
                        node.isEndOfWord = false;                                 // the word itself is gone …
                    } else {
                        int i = key.charAt(depth) - 'a';
                        node.child[i] = delete(node.child[i], key, depth + 1);
                    }
                    if (node.isEndOfWord || node.hasChild()) return node;         // … but this node still serves other words
                    return null;                                                  // useless node: unlink it
                }
                List<String> words() { List<String> out = new ArrayList<>(); dfs(root, new StringBuilder(), out); return out; }
                void dfs(TrieNode node, StringBuilder prefix, List<String> out) {
                    if (node.isEndOfWord) out.add(prefix.toString());
                    for (int i = 0; i < 26; i++)
                        if (node.child[i] != null) {
                            prefix.append((char) ('a' + i)); dfs(node.child[i], prefix, out); prefix.setLength(prefix.length() - 1);
                        }
                }
            }

            public static void main(String[] args) {
                Trie t = new Trie();
                for (String w : new String[]{"geeks", "geek", "bad", "bat", "cat", "cut"}) t.insert(w);
                t.delete("geeks"); System.out.println("after delete(geeks): geeks=" + t.search("geeks") + " geek=" + t.search("geek"));
                t.delete("bad");   System.out.println("after delete(bad): bad=" + t.search("bad") + " bat=" + t.search("bat"));
                t.delete("geek");  System.out.println("after delete(geek): geek=" + t.search("geek") + " startsWith(ge)=" + t.startsWith("ge"));
                System.out.println("words: " + String.join(" ", t.words()));
            }
        }
    ''', js='''
        class TrieNode {
            constructor() { this.child = new Array(26).fill(null); this.isEndOfWord = false; }
            hasChild() { return this.child.some(c => c !== null); }
        }

        class Trie {
            constructor() { this.root = new TrieNode(); }
            insert(key) {
                let node = this.root;
                for (const ch of key) {
                    const i = ch.charCodeAt(0) - 97;
                    if (node.child[i] === null) node.child[i] = new TrieNode();
                    node = node.child[i];
                }
                node.isEndOfWord = true;
            }
            walk(key) {
                let node = this.root;
                for (const ch of key) { node = node.child[ch.charCodeAt(0) - 97]; if (node === null) return null; }
                return node;
            }
            search(key) { const n = this.walk(key); return n !== null && n.isEndOfWord; }
            startsWith(p) { return this.walk(p) !== null; }

            delete(key) {
                const rec = (node, depth) => {                              // node to keep, or null to drop it
                    if (node === null) return null;
                    if (depth === key.length) {
                        node.isEndOfWord = false;                           // the word itself is gone …
                    } else {
                        const i = key.charCodeAt(depth) - 97;
                        node.child[i] = rec(node.child[i], depth + 1);
                    }
                    if (node.isEndOfWord || node.hasChild()) return node;   // … but this node still serves other words
                    return null;                                            // useless node: unlink it
                };
                this.root = rec(this.root, 0) ?? new TrieNode();
            }
            words() {
                const out = [];
                const dfs = (node, prefix) => {
                    if (node.isEndOfWord) out.push(prefix);
                    node.child.forEach((c, i) => { if (c !== null) dfs(c, prefix + String.fromCharCode(97 + i)); });
                };
                dfs(this.root, "");
                return out;
            }
        }

        const t = new Trie();
        for (const w of ["geeks", "geek", "bad", "bat", "cat", "cut"]) t.insert(w);
        t.delete("geeks"); console.log(`after delete(geeks): geeks=${t.search("geeks")} geek=${t.search("geek")}`);
        t.delete("bad");   console.log(`after delete(bad): bad=${t.search("bad")} bat=${t.search("bat")}`);
        t.delete("geek");  console.log(`after delete(geek): geek=${t.search("geek")} startsWith(ge)=${t.startsWith("ge")}`);
        console.log("words:", t.words().join(" "));
    ''')
    yield complexity("O(L) — one pass down and one pass back up", "O(L) recursion depth")
    yield pitfall("Only clearing `isEndOfWord` (\"lazy delete\") keeps `search` correct but leaves dead branches in memory and makes `startsWith(\"ge\")` wrongly return `true` after every `ge…` word is gone. Deleting a node that is still a word end or still has children breaks other words — check both conditions before unlinking.")

    yield section("Count distinct rows in a binary matrix", "table")
    yield p("Given a binary matrix (every entry `0` or `1`), count how many **distinct** rows it has.")
    yield io("matrix = [[1,0,0], [1,1,1], [1,0,0], [1,1,1]]", "2")
    yield p("**Naive:** for every row, compare it with every earlier row; count it if it matches none. `R` rows, each compared with up to `R` others, `C` entries per comparison.")
    yield snippet("py", '''
        def count_distinct_rows(matrix):
            res = 0
            for i, row in enumerate(matrix):
                if all(row != matrix[j] for j in range(i)):     # matches no earlier row → new
                    res += 1
            return res

        print(count_distinct_rows([[1, 0, 0], [1, 1, 1], [1, 0, 0], [1, 1, 1]]))
    ''', out="2")
    yield complexity("O(R² · C)", "O(1)")
    yield idea("Treat every row as a *word* over the alphabet `{0, 1}` and insert it into a **binary trie** (two children per node). Insertion of a row that is already present ends at a node that is already marked — so `insert` can report whether the row was new. Every row is inserted once: `O(R · C)` in total.")
    yield diagram('''
        rows: 1 0 0 / 1 1 1 / 1 0 0 / 1 1 1

                 (root)
                   │ 1
                   ●
              0 ┌──┴──┐ 1
                ●     ●
              0 │     │ 1
                ●*    ●*          two marked leaves → 2 distinct rows
    ''', "A binary trie of the rows: equal rows walk the same path and hit the same leaf")
    yield multi('''
        distinct rows: 2
    ''', py='''
        class Node:
            def __init__(self):
                self.child = [None, None]          # child[0] for a 0, child[1] for a 1
                self.is_end = False

        def insert_row(root, row):                 # True if the row was not present before
            node = root
            for bit in row:
                if node.child[bit] is None:
                    node.child[bit] = Node()
                node = node.child[bit]
            if node.is_end:
                return False                       # an identical row ended here already
            node.is_end = True
            return True

        def count_distinct_rows(matrix):
            root = Node()
            return sum(1 for row in matrix if insert_row(root, row))

        matrix = [[1, 0, 0], [1, 1, 1], [1, 0, 0], [1, 1, 1]]
        print("distinct rows:", count_distinct_rows(matrix))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            Node* child[2] = {nullptr, nullptr};   // child[0] for a 0, child[1] for a 1
            bool isEnd = false;
        };

        bool insertRow(Node* root, const vector<int>& row) {   // true if the row was not present before
            Node* node = root;
            for (int bit : row) {
                if (!node->child[bit]) node->child[bit] = new Node();
                node = node->child[bit];
            }
            if (node->isEnd) return false;                     // an identical row ended here already
            node->isEnd = true;
            return true;
        }

        int countDistinctRows(const vector<vector<int>>& matrix) {
            Node* root = new Node();
            int res = 0;
            for (const auto& row : matrix)
                if (insertRow(root, row)) res++;
            return res;
        }

        int main() {
            vector<vector<int>> matrix = {{1, 0, 0}, {1, 1, 1}, {1, 0, 0}, {1, 1, 1}};
            cout << "distinct rows: " << countDistinctRows(matrix) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                Node[] child = new Node[2];        // child[0] for a 0, child[1] for a 1
                boolean isEnd;
            }

            static boolean insertRow(Node root, int[] row) {   // true if the row was not present before
                Node node = root;
                for (int bit : row) {
                    if (node.child[bit] == null) node.child[bit] = new Node();
                    node = node.child[bit];
                }
                if (node.isEnd) return false;                  // an identical row ended here already
                node.isEnd = true;
                return true;
            }

            static int countDistinctRows(int[][] matrix) {
                Node root = new Node();
                int res = 0;
                for (int[] row : matrix)
                    if (insertRow(root, row)) res++;
                return res;
            }

            public static void main(String[] args) {
                int[][] matrix = {{1, 0, 0}, {1, 1, 1}, {1, 0, 0}, {1, 1, 1}};
                System.out.println("distinct rows: " + countDistinctRows(matrix));
            }
        }
    ''', js='''
        class Node {
            constructor() { this.child = [null, null]; this.isEnd = false; }   // child[0] for a 0, child[1] for a 1
        }

        function insertRow(root, row) {               // true if the row was not present before
            let node = root;
            for (const bit of row) {
                if (node.child[bit] === null) node.child[bit] = new Node();
                node = node.child[bit];
            }
            if (node.isEnd) return false;             // an identical row ended here already
            node.isEnd = true;
            return true;
        }

        function countDistinctRows(matrix) {
            const root = new Node();
            let res = 0;
            for (const row of matrix) if (insertRow(root, row)) res++;
            return res;
        }

        const matrix = [[1, 0, 0], [1, 1, 1], [1, 0, 0], [1, 1, 1]];
        console.log("distinct rows:", countDistinctRows(matrix));
    ''')
    yield complexity("O(R · C)", "O(R · C) for the trie in the worst case")
    yield note("A hash set of rows (as tuples / strings) also solves this in `O(R · C)` expected time and is shorter to write. The trie answers two things the set cannot: it can list the distinct rows in **sorted order**, and its memory is shared across rows with equal prefixes.", "Alternative")

    yield section("Interview Q&A", "message-question")
    yield qa("When would you choose a trie over a hash map?",
             "When the workload needs **prefix** operations — autocomplete, \"does any key start with…\", longest-prefix match (IP routing) — or **sorted** enumeration of the keys. For pure exact-match lookups a hash map is faster and uses far less memory.")
    yield qa("What is the space complexity of a trie, and how can it be reduced?",
             "Worst case `O(N · L · A)` for `N` words of length `L` over an alphabet of size `A`, because every node reserves `A` child slots. Reduce it with a hash map or sorted list of children per node (only the children that exist), with a **compressed trie / radix tree** that merges chains of single-child nodes, or with a **ternary search tree**.")
    yield qa("How do you implement autocomplete with a trie?",
             "Walk down the prefix (`O(P)`); if the walk fails there are no completions. Otherwise do a DFS from that node, appending characters, and emit every node with `isEndOfWord`. The DFS visits the children in alphabetical order, so the suggestions come out sorted. Store a *count* or *top-k* list in each node to rank suggestions without a full traversal.")
    yield qa("Why does a trie give lexicographic order for free?",
             "A pre-order traversal that visits the children in index order (`a` before `b` before `c`…) reaches every word end in dictionary order, because a shorter word is a prefix of the longer ones below it and siblings are visited alphabetically. This is also why `words()` above prints `bad bat cat cut geek geeks`.")
    yield qa("What goes wrong if `delete` just clears the end-of-word flag?",
             "Searches stay correct, but memory for dead branches is never reclaimed, and `startsWith` returns `true` for prefixes that no longer lead to any word. Proper deletion removes nodes bottom-up while they are unmarked and childless, stopping at the first node another word still uses.")


@topic(G, "disjoint_set", "Disjoint Set", "circles-relation")
def _():
    yield lead("A disjoint-set (union–find) structure keeps track of a collection of elements partitioned into **non-overlapping groups**, and answers two questions almost instantly: *which group is x in?* and *merge the groups of x and y*. It is the engine behind Kruskal's MST, cycle detection and dynamic connectivity.")
    yield define("Disjoint set (union–find)", "a data structure over elements `0 … n-1` that maintains a partition into disjoint sets, each identified by one **representative** element, supporting `find(x)` → representative of `x`'s set, and `union(x, y)` → merge the two sets containing `x` and `y`.")

    yield section("The problem: dynamic connectivity", "link")
    yield p("`n` people are initially strangers. Two operations arrive in any order: `makeFriends(x, y)` — now `x` and `y` are in the same friend circle (friendship is transitive) — and `areFriends(x, y)` — are they in the same circle? Answer the queries as they come, with no knowledge of future operations.")
    yield io("n = 4; makeFriends(0, 1), makeFriends(1, 3), areFriends(0, 2), areFriends(0, 1), areFriends(0, 3)", "No Yes Yes")
    yield table(
        ["Approach", "`makeFriends`", "`areFriends`", "Problem"],
        ["Adjacency list + DFS/BFS", "O(1)", "O(n + m) — traverse the graph", "a query must explore the whole component"],
        ["Adjacency matrix + DFS/BFS", "O(1)", "O(n²)", "same, and n² memory"],
        ["Store the component id of every node", "Θ(n) — relabel one whole component", "Θ(1)", "every merge rewrites up to n labels"],
        ["**Disjoint set**", "**≈ O(1)** amortised", "**≈ O(1)** amortised", "—"],
    )
    yield idea("Represent every set as a **tree**: each element stores its parent, the root is the set's representative. `find(x)` climbs to the root. `union(x, y)` makes one root the parent of the other. Two elements are in the same set exactly when they climb to the same root.")
    yield diagram('''
        initially                 makeFriends(0, 1)        makeFriends(1, 3)
        parent: 0 1 2 3           parent: 0 0 2 3          parent: 0 0 2 0

        (0) (1) (2) (3)            (0)   (2) (3)              (0)    (2)
                                    │                         / \\
                                   (1)                      (1) (3)

        areFriends(0, 2): find(0)=0, find(2)=2 → No
        areFriends(0, 3): find(0)=0, find(3)=0 → Yes
    ''', "Each set is a tree stored in a parent array; a root is its own parent")

    yield section("Basic implementation: parent array", "list-numbers")
    yield steps(
        ("`make_set`", "`parent[i] = i` for every element — `n` singleton sets."),
        ("`find(x)`", "Follow `parent` links until reaching an element that is its own parent; that root is the representative."),
        ("`union(x, y)`", "`rx = find(x)`, `ry = find(y)`; if they differ, `parent[ry] = rx`."),
        ("`areFriends(x, y)`", "`find(x) == find(y)`."),
    )
    yield multi('''
        areFriends(0, 2): No
        areFriends(0, 1): Yes
        areFriends(0, 3): Yes
        parent: 0 0 2 0
    ''', py='''
        class DisjointSet:
            def __init__(self, n):
                self.parent = list(range(n))       # every element starts as its own set

            def find(self, x):
                while self.parent[x] != x:         # climb to the root
                    x = self.parent[x]
                return x

            def union(self, x, y):
                rx, ry = self.find(x), self.find(y)
                if rx != ry:
                    self.parent[ry] = rx           # hang one tree under the other root

            def are_friends(self, x, y):
                return self.find(x) == self.find(y)

        ds = DisjointSet(4)
        ds.union(0, 1)                             # makeFriends
        ds.union(1, 3)
        for x, y in [(0, 2), (0, 1), (0, 3)]:
            print(f"areFriends({x}, {y}):", "Yes" if ds.are_friends(x, y) else "No")
        print("parent:", " ".join(map(str, ds.parent)))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        class DisjointSet {
            vector<int> parent;
        public:
            DisjointSet(int n) : parent(n) {
                for (int i = 0; i < n; i++) parent[i] = i;      // every element starts as its own set
            }
            int find(int x) {
                while (parent[x] != x) x = parent[x];          // climb to the root
                return x;
            }
            void unite(int x, int y) {                         // "union" is a C++ keyword
                int rx = find(x), ry = find(y);
                if (rx != ry) parent[ry] = rx;                 // hang one tree under the other root
            }
            bool areFriends(int x, int y) { return find(x) == find(y); }
            const vector<int>& parents() const { return parent; }
        };

        int main() {
            DisjointSet ds(4);
            ds.unite(0, 1);                                    // makeFriends
            ds.unite(1, 3);
            int queries[3][2] = {{0, 2}, {0, 1}, {0, 3}};
            for (auto& q : queries)
                cout << "areFriends(" << q[0] << ", " << q[1] << "): " << (ds.areFriends(q[0], q[1]) ? "Yes" : "No") << "\\n";
            cout << "parent:";
            for (int p : ds.parents()) cout << " " << p;
            cout << "\\n";
        }
    ''', java='''
        public class Main {
            static class DisjointSet {
                int[] parent;
                DisjointSet(int n) {
                    parent = new int[n];
                    for (int i = 0; i < n; i++) parent[i] = i;   // every element starts as its own set
                }
                int find(int x) {
                    while (parent[x] != x) x = parent[x];       // climb to the root
                    return x;
                }
                void union(int x, int y) {
                    int rx = find(x), ry = find(y);
                    if (rx != ry) parent[ry] = rx;              // hang one tree under the other root
                }
                boolean areFriends(int x, int y) { return find(x) == find(y); }
            }

            public static void main(String[] args) {
                DisjointSet ds = new DisjointSet(4);
                ds.union(0, 1);                                 // makeFriends
                ds.union(1, 3);
                int[][] queries = {{0, 2}, {0, 1}, {0, 3}};
                for (int[] q : queries)
                    System.out.println("areFriends(" + q[0] + ", " + q[1] + "): " + (ds.areFriends(q[0], q[1]) ? "Yes" : "No"));
                StringBuilder sb = new StringBuilder("parent:");
                for (int p : ds.parent) sb.append(' ').append(p);
                System.out.println(sb);
            }
        }
    ''', js='''
        class DisjointSet {
            constructor(n) { this.parent = Array.from({ length: n }, (_, i) => i); }   // every element is its own set
            find(x) {
                while (this.parent[x] !== x) x = this.parent[x];   // climb to the root
                return x;
            }
            union(x, y) {
                const rx = this.find(x), ry = this.find(y);
                if (rx !== ry) this.parent[ry] = rx;               // hang one tree under the other root
            }
            areFriends(x, y) { return this.find(x) === this.find(y); }
        }

        const ds = new DisjointSet(4);
        ds.union(0, 1);                                            // makeFriends
        ds.union(1, 3);
        for (const [x, y] of [[0, 2], [0, 1], [0, 3]])
            console.log(`areFriends(${x}, ${y}):`, ds.areFriends(x, y) ? "Yes" : "No");
        console.log("parent:", ds.parent.join(" "));
    ''')
    yield complexity("O(n) worst case per operation — the tree can degenerate into a chain", "O(n)")
    yield pitfall("Naive union can build a tree that is a straight line: `union(1,0), union(2,1), union(3,2), …` makes `find(0)` walk `n` steps. The two optimisations below exist to keep every tree shallow.")

    yield section("Union by rank (or by size)", "arrows-sort")
    yield p("Keep an extra array `rank` that stores an upper bound on the **height** of each root's tree. When uniting two roots, make the root of the **shorter** tree a child of the taller one — the height does not grow. Only when both have equal rank does the merged tree get one level taller.")
    yield diagram('''
        rank[rx] < rank[ry]          rank[rx] > rank[ry]          rank[rx] == rank[ry]
        parent[rx] = ry              parent[ry] = rx              parent[ry] = rx; rank[rx] += 1

            (ry)                         (rx)                         (rx)  rank+1
           /  │  \\                      /  │  \\                      /  │  \\
         ...  ... (rx)                ...  ... (ry)                 ...  ... (ry)
    ''', "Attach the shallower tree under the deeper root — height grows only on a tie")
    yield table(
        ["Variant", "What is compared", "Guarantee"],
        ["Union by rank", "height bound of the two trees", "height ≤ `log₂ n` → `find` is `O(log n)`"],
        ["Union by size", "number of elements in the two trees (attach smaller under larger)", "same `O(log n)` bound; the size array is useful in its own right (component sizes)"],
    )
    yield note("With union by rank alone, a tree of height `h` must contain at least `2^h` elements (each rank increase doubles the minimum size), so no tree is deeper than `log₂ n`.", "Why log n")

    yield section("Path compression", "arrow-up")
    yield p("`find(x)` already visits every node on the path from `x` to the root. While it is there, **re-point each of them directly at the root** — the next `find` on any of them is a single step. The parent array is only ever changed in a way that keeps the same sets.")
    yield diagram('''
        before find(6)                      after find(6)

             (0)                               (0)
             / \\                             / | \\
           (1) (2)                         (1)(2)(4)        6 and 4 now point straight at 0;
                 │                              │   \\       5 still points at 4 (it was not on the path)
                (4)                            (3)  (6) …
               /   \\
             (5)   (6)
    ''', "Path compression flattens the path that find() walks")
    yield io("n = 7; union(0,1) union(2,3) union(4,5) union(1,3) union(5,6) union(3,5); then find(6)", "parent array before / after shows the compression; connected(2, 5) = Yes")
    yield multi('''
        parent after unions: 0 0 0 0 0 4 4
        find(6) = 0
        parent after find(6): 0 0 0 0 0 4 0
        connected(2, 5): Yes
        connected(3, 6): Yes
        components: 1
    ''', py='''
        class DisjointSet:
            def __init__(self, n):
                self.parent = list(range(n))
                self.rank = [0] * n                    # upper bound on the height of each root's tree
                self.components = n

            def find(self, x):
                if self.parent[x] != x:
                    self.parent[x] = self.find(self.parent[x])   # path compression: point straight at the root
                return self.parent[x]

            def union(self, x, y):
                rx, ry = self.find(x), self.find(y)
                if rx == ry:
                    return False                       # already in the same set
                if self.rank[rx] < self.rank[ry]:      # union by rank: shallower tree goes under the deeper root
                    rx, ry = ry, rx
                self.parent[ry] = rx
                if self.rank[rx] == self.rank[ry]:
                    self.rank[rx] += 1                 # only a tie makes the tree taller
                self.components -= 1
                return True

            def connected(self, x, y):
                return self.find(x) == self.find(y)

        ds = DisjointSet(7)
        for x, y in [(0, 1), (2, 3), (4, 5), (1, 3), (5, 6), (3, 5)]:
            ds.union(x, y)
        print("parent after unions:", " ".join(map(str, ds.parent)))
        print("find(6) =", ds.find(6))
        print("parent after find(6):", " ".join(map(str, ds.parent)))
        print("connected(2, 5):", "Yes" if ds.connected(2, 5) else "No")
        print("connected(3, 6):", "Yes" if ds.connected(3, 6) else "No")
        print("components:", ds.components)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        class DisjointSet {
            vector<int> parent, rnk;                      // rnk = upper bound on the height of each root's tree
        public:
            int components;
            DisjointSet(int n) : parent(n), rnk(n, 0), components(n) {
                for (int i = 0; i < n; i++) parent[i] = i;
            }
            int find(int x) {
                if (parent[x] != x) parent[x] = find(parent[x]);   // path compression: point straight at the root
                return parent[x];
            }
            bool unite(int x, int y) {
                int rx = find(x), ry = find(y);
                if (rx == ry) return false;               // already in the same set
                if (rnk[rx] < rnk[ry]) swap(rx, ry);      // union by rank: shallower tree goes under the deeper root
                parent[ry] = rx;
                if (rnk[rx] == rnk[ry]) rnk[rx]++;        // only a tie makes the tree taller
                components--;
                return true;
            }
            bool connected(int x, int y) { return find(x) == find(y); }
            void printParents(const string& label) {
                cout << label << ":";
                for (int p : parent) cout << " " << p;
                cout << "\\n";
            }
        };

        int main() {
            DisjointSet ds(7);
            int edges[6][2] = {{0, 1}, {2, 3}, {4, 5}, {1, 3}, {5, 6}, {3, 5}};
            for (auto& e : edges) ds.unite(e[0], e[1]);
            ds.printParents("parent after unions");
            cout << "find(6) = " << ds.find(6) << "\\n";
            ds.printParents("parent after find(6)");
            cout << "connected(2, 5): " << (ds.connected(2, 5) ? "Yes" : "No") << "\\n";
            cout << "connected(3, 6): " << (ds.connected(3, 6) ? "Yes" : "No") << "\\n";
            cout << "components: " << ds.components << "\\n";
        }
    ''', java='''
        public class Main {
            static class DisjointSet {
                int[] parent, rank;                           // rank = upper bound on the height of each root's tree
                int components;
                DisjointSet(int n) {
                    parent = new int[n]; rank = new int[n]; components = n;
                    for (int i = 0; i < n; i++) parent[i] = i;
                }
                int find(int x) {
                    if (parent[x] != x) parent[x] = find(parent[x]);   // path compression: point straight at the root
                    return parent[x];
                }
                boolean union(int x, int y) {
                    int rx = find(x), ry = find(y);
                    if (rx == ry) return false;               // already in the same set
                    if (rank[rx] < rank[ry]) { int t = rx; rx = ry; ry = t; }   // union by rank: shallower under deeper
                    parent[ry] = rx;
                    if (rank[rx] == rank[ry]) rank[rx]++;     // only a tie makes the tree taller
                    components--;
                    return true;
                }
                boolean connected(int x, int y) { return find(x) == find(y); }
                String parents() {
                    StringBuilder sb = new StringBuilder();
                    for (int p : parent) sb.append(' ').append(p);
                    return sb.toString();
                }
            }

            public static void main(String[] args) {
                DisjointSet ds = new DisjointSet(7);
                int[][] edges = {{0, 1}, {2, 3}, {4, 5}, {1, 3}, {5, 6}, {3, 5}};
                for (int[] e : edges) ds.union(e[0], e[1]);
                System.out.println("parent after unions:" + ds.parents());
                System.out.println("find(6) = " + ds.find(6));
                System.out.println("parent after find(6):" + ds.parents());
                System.out.println("connected(2, 5): " + (ds.connected(2, 5) ? "Yes" : "No"));
                System.out.println("connected(3, 6): " + (ds.connected(3, 6) ? "Yes" : "No"));
                System.out.println("components: " + ds.components);
            }
        }
    ''', js='''
        class DisjointSet {
            constructor(n) {
                this.parent = Array.from({ length: n }, (_, i) => i);
                this.rank = new Array(n).fill(0);             // upper bound on the height of each root's tree
                this.components = n;
            }
            find(x) {
                if (this.parent[x] !== x) this.parent[x] = this.find(this.parent[x]);   // path compression
                return this.parent[x];
            }
            union(x, y) {
                let rx = this.find(x), ry = this.find(y);
                if (rx === ry) return false;                  // already in the same set
                if (this.rank[rx] < this.rank[ry]) [rx, ry] = [ry, rx];   // union by rank: shallower under deeper
                this.parent[ry] = rx;
                if (this.rank[rx] === this.rank[ry]) this.rank[rx]++;     // only a tie makes the tree taller
                this.components--;
                return true;
            }
            connected(x, y) { return this.find(x) === this.find(y); }
        }

        const ds = new DisjointSet(7);
        for (const [x, y] of [[0, 1], [2, 3], [4, 5], [1, 3], [5, 6], [3, 5]]) ds.union(x, y);
        console.log("parent after unions:", ds.parent.join(" "));
        console.log("find(6) =", ds.find(6));
        console.log("parent after find(6):", ds.parent.join(" "));
        console.log("connected(2, 5):", ds.connected(2, 5) ? "Yes" : "No");
        console.log("connected(3, 6):", ds.connected(3, 6) ? "Yes" : "No");
        console.log("components:", ds.components);
    ''')
    yield complexity("O(α(n)) amortised per operation — effectively constant", "O(n)")
    yield table(
        ["Optimisations used", "Amortised cost per operation"],
        ["none", "O(n)"],
        ["union by rank only", "O(log n)"],
        ["path compression only", "O(log n)"],
        ["**both**", "**O(α(n))** — the inverse Ackermann function, `≤ 4` for every `n` that fits in the universe"],
    )
    yield note("After path compression the `rank` values are no longer exact heights — they are only upper bounds. That is fine: the proof of the `log n` bound only needs ranks to be upper bounds, and leaving them untouched keeps `find` simple.", "Rank ≠ height")
    yield pitfall("The recursive `find` compresses the path but recurses once per level. Python's recursion limit (1000) can be hit on adversarial inputs *before* the first compression; an iterative two-pass version (first find the root, then re-point every node on the path) avoids that.")

    yield section("Detect a cycle in an undirected graph", "repeat")
    yield p("Process the edges one by one. For edge `(u, v)`: if `u` and `v` are already in the same set, this edge closes a **cycle**; otherwise unite them. This is also exactly the test Kruskal's algorithm uses to decide whether an edge may join the spanning tree.")
    yield io("n = 4, edges = (0,1) (1,2) (2,3) (3,1)", "cycle found at edge 3-1")
    yield idea("An edge between two vertices that are already connected creates a second path between them — a cycle. Union–find answers \"already connected?\" in near-constant time, so the whole scan is `O(E · α(V))`.")
    yield multi('''
        edge 0-1: joined
        edge 1-2: joined
        edge 2-3: joined
        edge 3-1: already connected → cycle
        graph has a cycle: Yes
    ''', py='''
        class DisjointSet:
            def __init__(self, n):
                self.parent = list(range(n))
                self.rank = [0] * n

            def find(self, x):
                if self.parent[x] != x:
                    self.parent[x] = self.find(self.parent[x])
                return self.parent[x]

            def union(self, x, y):
                rx, ry = self.find(x), self.find(y)
                if rx == ry:
                    return False
                if self.rank[rx] < self.rank[ry]:
                    rx, ry = ry, rx
                self.parent[ry] = rx
                if self.rank[rx] == self.rank[ry]:
                    self.rank[rx] += 1
                return True

        def has_cycle(n, edges):
            ds = DisjointSet(n)
            for u, v in edges:
                if ds.find(u) == ds.find(v):                 # already connected → this edge closes a cycle
                    print(f"edge {u}-{v}: already connected → cycle")
                    return True
                ds.union(u, v)
                print(f"edge {u}-{v}: joined")
            return False

        edges = [(0, 1), (1, 2), (2, 3), (3, 1)]
        print("graph has a cycle:", "Yes" if has_cycle(4, edges) else "No")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct DisjointSet {
            vector<int> parent, rnk;
            DisjointSet(int n) : parent(n), rnk(n, 0) { for (int i = 0; i < n; i++) parent[i] = i; }
            int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
            bool unite(int x, int y) {
                int rx = find(x), ry = find(y);
                if (rx == ry) return false;
                if (rnk[rx] < rnk[ry]) swap(rx, ry);
                parent[ry] = rx;
                if (rnk[rx] == rnk[ry]) rnk[rx]++;
                return true;
            }
        };

        bool hasCycle(int n, const vector<pair<int,int>>& edges) {
            DisjointSet ds(n);
            for (auto [u, v] : edges) {
                if (ds.find(u) == ds.find(v)) {              // already connected → this edge closes a cycle
                    cout << "edge " << u << "-" << v << ": already connected → cycle\\n";
                    return true;
                }
                ds.unite(u, v);
                cout << "edge " << u << "-" << v << ": joined\\n";
            }
            return false;
        }

        int main() {
            vector<pair<int,int>> edges = {{0, 1}, {1, 2}, {2, 3}, {3, 1}};
            bool cyc = hasCycle(4, edges);
            cout << "graph has a cycle: " << (cyc ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        public class Main {
            static class DisjointSet {
                int[] parent, rank;
                DisjointSet(int n) { parent = new int[n]; rank = new int[n]; for (int i = 0; i < n; i++) parent[i] = i; }
                int find(int x) { return parent[x] == x ? x : (parent[x] = find(parent[x])); }
                boolean union(int x, int y) {
                    int rx = find(x), ry = find(y);
                    if (rx == ry) return false;
                    if (rank[rx] < rank[ry]) { int t = rx; rx = ry; ry = t; }
                    parent[ry] = rx;
                    if (rank[rx] == rank[ry]) rank[rx]++;
                    return true;
                }
            }

            static boolean hasCycle(int n, int[][] edges) {
                DisjointSet ds = new DisjointSet(n);
                for (int[] e : edges) {
                    int u = e[0], v = e[1];
                    if (ds.find(u) == ds.find(v)) {              // already connected → this edge closes a cycle
                        System.out.println("edge " + u + "-" + v + ": already connected → cycle");
                        return true;
                    }
                    ds.union(u, v);
                    System.out.println("edge " + u + "-" + v + ": joined");
                }
                return false;
            }

            public static void main(String[] args) {
                int[][] edges = {{0, 1}, {1, 2}, {2, 3}, {3, 1}};
                boolean cyc = hasCycle(4, edges);
                System.out.println("graph has a cycle: " + (cyc ? "Yes" : "No"));
            }
        }
    ''', js='''
        class DisjointSet {
            constructor(n) { this.parent = Array.from({ length: n }, (_, i) => i); this.rank = new Array(n).fill(0); }
            find(x) { return this.parent[x] === x ? x : (this.parent[x] = this.find(this.parent[x])); }
            union(x, y) {
                let rx = this.find(x), ry = this.find(y);
                if (rx === ry) return false;
                if (this.rank[rx] < this.rank[ry]) [rx, ry] = [ry, rx];
                this.parent[ry] = rx;
                if (this.rank[rx] === this.rank[ry]) this.rank[rx]++;
                return true;
            }
        }

        function hasCycle(n, edges) {
            const ds = new DisjointSet(n);
            for (const [u, v] of edges) {
                if (ds.find(u) === ds.find(v)) {                 // already connected → this edge closes a cycle
                    console.log(`edge ${u}-${v}: already connected → cycle`);
                    return true;
                }
                ds.union(u, v);
                console.log(`edge ${u}-${v}: joined`);
            }
            return false;
        }

        const edges = [[0, 1], [1, 2], [2, 3], [3, 1]];
        const cyc = hasCycle(4, edges);
        console.log("graph has a cycle:", cyc ? "Yes" : "No");
    ''')
    yield complexity("O(E · α(V))", "O(V)")
    yield pitfall("This test is for **undirected** graphs only. In a directed graph the edges `a → b` and `c → b` put `a`, `b`, `c` in one set without any cycle; directed cycle detection needs DFS with colours (see Graphs).")

    yield section("Where disjoint sets are used", "apps")
    yield cards(
        ("Kruskal's MST", "Sort edges by weight; add an edge iff its endpoints are in different sets.", "topology-star"),
        ("Connected components", "Union every edge; the number of roots is the number of components — `components` above.", "circles"),
        ("Cycle detection", "An edge inside one set closes a cycle (above).", "repeat"),
        ("Dynamic connectivity", "Answer \"are x and y connected?\" while edges keep arriving — the friends problem.", "link"),
        ("Image / grid regions", "Flood-fill alternatives: unite neighbouring pixels of the same colour (number of islands).", "grid-dots"),
        ("Percolation, LCA (Tarjan), equivalence classes", "Any problem that merges groups and never splits them.", "puzzle"),
        cols=3,
    )
    yield warn("Union–find supports **merge only** — there is no efficient `split`. If sets must be separated again, it is the wrong structure (use offline processing in reverse, or a link-cut tree).")

    yield section("Interview Q&A", "message-question")
    yield qa("What is the amortised complexity of union–find with both optimisations, and what does α(n) mean?",
             "`O(α(n))` per operation amortised, where `α` is the **inverse Ackermann function** — it grows so slowly that `α(n) ≤ 4` for any `n` below `2^65536`. In practice every operation is constant time. Tarjan proved this bound is tight for the structure.")
    yield qa("Union by rank vs union by size — any difference?",
             "Both guarantee `O(log n)` tree height and `O(α(n))` with path compression. Size is more useful when you also need component sizes (e.g. \"size of the largest group\"); rank is a smaller number to store. Never attach arbitrarily — that is what allows `O(n)` chains.")
    yield qa("How does path compression work and why doesn't it break the sets?",
             "During `find(x)`, every node on the path to the root gets `parent[node] = root`. Membership is defined by *which root you reach*, not by the exact path, so re-pointing nodes at the same root changes nothing about the sets while making future finds shorter.")
    yield qa("How would you detect a cycle in an undirected graph with union–find?",
             "Process the edges; for `(u, v)` check `find(u) == find(v)`. Equal → the edge connects two already-connected vertices → cycle. Otherwise `union(u, v)`. Total `O(E · α(V))`. It also counts components: `V − (number of successful unions)`.")
    yield qa("Why does Kruskal's algorithm rely on union–find?",
             "Kruskal adds the cheapest edge that does not form a cycle. The cycle test on each of `E` sorted edges would cost `O(V)` with DFS; union–find makes it near constant, giving `O(E log E)` total dominated by the sort.")


@topic(G, "segment_tree", "Segment Tree", "binary-tree-2")
def _():
    yield lead("A segment tree answers **range queries** (sum, min, max, …) over an array and **updates** single elements, both in `O(log n)`. It is the structure to use when both operations are frequent, because a plain array makes queries slow and a prefix-sum array makes updates slow.")
    yield define("Segment tree", "a binary tree over a fixed-size array in which every node stores an aggregate (e.g. the sum) of one contiguous segment: the root covers the whole array, each child covers one half of its parent's segment, and the leaves are the individual elements.")
    yield diagram('''
        arr = [10, 20, 30, 40]            index:  0   1   2   3

                        [0..3] = 100                 tree[0]
                       /            \\
              [0..1] = 30          [2..3] = 70        tree[1]  tree[2]
              /       \\            /       \\
        [0]=10     [1]=20    [2]=30     [3]=40        tree[3] tree[4] tree[5] tree[6]

        tree array:  100  30  70  10  20  30  40
                      0    1   2   3   4   5   6        children of i are 2i+1 and 2i+2
    ''', "Segment tree of sums over [10, 20, 30, 40], stored in an array like a heap")
    yield io("arr = [10, 20, 30, 40, 50]; getSum(0, 2); getSum(1, 3); update(1, 60); getSum(0, 2)", "60, 90, then 100")

    yield section("Why not a plain array or prefix sums?", "scale")
    yield p("Suppose `x` operations arrive, of which a quarter are range-sum queries and three quarters are updates. With a plain array queries cost `O(n)` and updates `O(1)`, so the average is `(x/4 · O(n) + 3x/4 · O(1)) / x = O(n)`. With a prefix-sum array it is the reverse — queries `O(1)`, updates `O(n)` — and the average is again `O(n)`. A segment tree makes **both** `O(log n)`.")
    yield table(
        ["Structure", "Range sum", "Point update", "Preprocessing", "Space"],
        ["Plain array", "O(n)", "O(1)", "—", "O(n)"],
        ["Prefix-sum array", "O(1)", "O(n)", "O(n)", "O(n)"],
        ["**Segment tree**", "**O(log n)**", "**O(log n)**", "O(n)", "O(n) (≈ 4n slots)"],
        ["Binary indexed tree", "O(log n)", "O(log n)", "O(n log n) (O(n) possible)", "O(n) (n + 1 slots)"],
    )
    yield note("Segment trees work for any **associative** aggregate: sum, min, max, gcd, XOR, number of zeros, … Replace the `+` in the three functions below and nothing else changes. They also extend to range updates with lazy propagation — the binary indexed tree does not handle min/max.")

    yield section("Size of the tree array", "ruler")
    yield p("Children of node `i` live at `2i + 1` and `2i + 2`, so the tree is stored in a plain array with no pointers. How large must it be?")
    yield ul(
        "If `n` is a power of two the tree is perfect: `2n − 1` nodes.",
        "Otherwise let `x` be the smallest power of two **greater than** `n`; the tree needs at most `2x − 1` slots (some stay unused).",
        "In practice allocate `4n` — it is always enough (`2x − 1 < 4n`) and saves computing `x`.",
    )
    yield formula("size = 2 · 2^⌈log₂ n⌉ − 1   (≤ 4n)")
    yield example("`n = 5` → `x = 8` → at most `15` slots; `n = 4` → exactly `7` slots, all used.")

    yield section("Constructing the segment tree", "hammer")
    yield io("arr = [10, 20, 30, 40]", "tree = [100, 30, 70, 10, 20, 30, 40]")
    yield idea("Build recursively: if the segment is a single element store it; otherwise build the left half and the right half, then store their sum. Every node is written exactly once — `O(n)`.")
    yield steps(
        ("`build(ss, se, si)`", "`ss`/`se` = segment start/end in `arr`, `si` = index of this node in `tree`."),
        ("Leaf", "`ss == se` → `tree[si] = arr[ss]`."),
        ("Internal node", "`mid = (ss + se) / 2`; `tree[si] = build(ss, mid, 2si+1) + build(mid+1, se, 2si+2)`."),
    )
    yield multi('''
        tree: 100 30 70 10 20 30 40
    ''', py='''
        def build(arr, tree, ss, se, si):
            if ss == se:                                        # leaf: a single element
                tree[si] = arr[ss]
                return tree[si]
            mid = (ss + se) // 2
            tree[si] = build(arr, tree, ss, mid, 2 * si + 1) + build(arr, tree, mid + 1, se, 2 * si + 2)
            return tree[si]                                     # parent = left sum + right sum

        def tree_size(n):
            x = 1
            while x < n:                                        # smallest power of two ≥ n
                x *= 2
            return 2 * x - 1

        arr = [10, 20, 30, 40]
        tree = [0] * tree_size(len(arr))
        build(arr, tree, 0, len(arr) - 1, 0)
        print("tree:", " ".join(map(str, tree)))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int build(const vector<int>& arr, vector<int>& tree, int ss, int se, int si) {
            if (ss == se) return tree[si] = arr[ss];            // leaf: a single element
            int mid = (ss + se) / 2;
            return tree[si] = build(arr, tree, ss, mid, 2 * si + 1)
                            + build(arr, tree, mid + 1, se, 2 * si + 2);   // parent = left sum + right sum
        }

        int treeSize(int n) {
            int x = 1;
            while (x < n) x *= 2;                                // smallest power of two ≥ n
            return 2 * x - 1;
        }

        int main() {
            vector<int> arr = {10, 20, 30, 40};
            int n = arr.size();
            vector<int> tree(treeSize(n), 0);
            build(arr, tree, 0, n - 1, 0);
            cout << "tree:";
            for (int v : tree) cout << " " << v;
            cout << "\\n";
        }
    ''', java='''
        public class Main {
            static int build(int[] arr, int[] tree, int ss, int se, int si) {
                if (ss == se) return tree[si] = arr[ss];        // leaf: a single element
                int mid = (ss + se) / 2;
                return tree[si] = build(arr, tree, ss, mid, 2 * si + 1)
                                + build(arr, tree, mid + 1, se, 2 * si + 2);   // parent = left sum + right sum
            }

            static int treeSize(int n) {
                int x = 1;
                while (x < n) x *= 2;                            // smallest power of two ≥ n
                return 2 * x - 1;
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 30, 40};
                int[] tree = new int[treeSize(arr.length)];
                build(arr, tree, 0, arr.length - 1, 0);
                StringBuilder sb = new StringBuilder("tree:");
                for (int v : tree) sb.append(' ').append(v);
                System.out.println(sb);
            }
        }
    ''', js='''
        function build(arr, tree, ss, se, si) {
            if (ss === se) return (tree[si] = arr[ss]);         // leaf: a single element
            const mid = Math.floor((ss + se) / 2);
            return (tree[si] = build(arr, tree, ss, mid, 2 * si + 1)
                             + build(arr, tree, mid + 1, se, 2 * si + 2));   // parent = left sum + right sum
        }

        function treeSize(n) {
            let x = 1;
            while (x < n) x *= 2;                                // smallest power of two ≥ n
            return 2 * x - 1;
        }

        const arr = [10, 20, 30, 40];
        const tree = new Array(treeSize(arr.length)).fill(0);
        build(arr, tree, 0, arr.length - 1, 0);
        console.log("tree:", tree.join(" "));
    ''')
    yield complexity("O(n) — each of the ≈ 2n nodes is computed once", "O(n)")

    yield section("Range query", "search")
    yield io("arr = [10, 20, 30, 40]; getSum(0, 2)", "60", "getSum(1, 3)", "90")
    yield idea("Walk down from the root. A node's segment relates to the query range `[qs, qe]` in one of three ways: **completely inside** → return its stored sum without going deeper; **completely outside** → contribute `0`; **partially overlapping** → recurse into both children and add.")
    yield diagram('''
        getSum(1, 2) on [10, 20, 30, 40]

                 [0..3]  partial overlap → recurse
                /      \\
          [0..1] partial  [2..3] partial
          /    \\          /    \\
        [0]    [1]      [2]    [3]
        outside inside  inside outside
          0     20       30      0        → 20 + 30 = 50
    ''', "The three cases — at most two nodes per level are partially overlapped, so the query touches O(log n) nodes")
    yield multi('''
        tree: 100 30 70 10 20 30 40
        sum(0, 2): 60
        sum(1, 3): 90
        sum(2, 2): 30
    ''', py='''
        def build(arr, tree, ss, se, si):
            if ss == se:
                tree[si] = arr[ss]
                return tree[si]
            mid = (ss + se) // 2
            tree[si] = build(arr, tree, ss, mid, 2 * si + 1) + build(arr, tree, mid + 1, se, 2 * si + 2)
            return tree[si]

        def get_sum_rec(tree, qs, qe, ss, se, si):
            if qe < ss or qs > se:                              # segment completely outside the query
                return 0
            if qs <= ss and se <= qe:                           # segment completely inside the query
                return tree[si]
            mid = (ss + se) // 2                                # partial overlap: ask both children
            return get_sum_rec(tree, qs, qe, ss, mid, 2 * si + 1) + get_sum_rec(tree, qs, qe, mid + 1, se, 2 * si + 2)

        def get_sum(tree, n, qs, qe):
            if qs < 0 or qe > n - 1 or qs > qe:
                raise ValueError("invalid range")
            return get_sum_rec(tree, qs, qe, 0, n - 1, 0)

        arr = [10, 20, 30, 40]
        n = len(arr)
        x = 1
        while x < n:
            x *= 2
        tree = [0] * (2 * x - 1)
        build(arr, tree, 0, n - 1, 0)
        print("tree:", " ".join(map(str, tree)))
        for qs, qe in [(0, 2), (1, 3), (2, 2)]:
            print(f"sum({qs}, {qe}):", get_sum(tree, n, qs, qe))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <stdexcept>
        using namespace std;

        int build(const vector<int>& arr, vector<int>& tree, int ss, int se, int si) {
            if (ss == se) return tree[si] = arr[ss];
            int mid = (ss + se) / 2;
            return tree[si] = build(arr, tree, ss, mid, 2 * si + 1) + build(arr, tree, mid + 1, se, 2 * si + 2);
        }

        int getSumRec(const vector<int>& tree, int qs, int qe, int ss, int se, int si) {
            if (qe < ss || qs > se) return 0;                   // segment completely outside the query
            if (qs <= ss && se <= qe) return tree[si];          // segment completely inside the query
            int mid = (ss + se) / 2;                             // partial overlap: ask both children
            return getSumRec(tree, qs, qe, ss, mid, 2 * si + 1) + getSumRec(tree, qs, qe, mid + 1, se, 2 * si + 2);
        }

        int getSum(const vector<int>& tree, int n, int qs, int qe) {
            if (qs < 0 || qe > n - 1 || qs > qe) throw invalid_argument("invalid range");
            return getSumRec(tree, qs, qe, 0, n - 1, 0);
        }

        int main() {
            vector<int> arr = {10, 20, 30, 40};
            int n = arr.size(), x = 1;
            while (x < n) x *= 2;
            vector<int> tree(2 * x - 1, 0);
            build(arr, tree, 0, n - 1, 0);
            cout << "tree:";
            for (int v : tree) cout << " " << v;
            cout << "\\n";
            int queries[3][2] = {{0, 2}, {1, 3}, {2, 2}};
            for (auto& q : queries) cout << "sum(" << q[0] << ", " << q[1] << "): " << getSum(tree, n, q[0], q[1]) << "\\n";
        }
    ''', java='''
        public class Main {
            static int build(int[] arr, int[] tree, int ss, int se, int si) {
                if (ss == se) return tree[si] = arr[ss];
                int mid = (ss + se) / 2;
                return tree[si] = build(arr, tree, ss, mid, 2 * si + 1) + build(arr, tree, mid + 1, se, 2 * si + 2);
            }

            static int getSumRec(int[] tree, int qs, int qe, int ss, int se, int si) {
                if (qe < ss || qs > se) return 0;               // segment completely outside the query
                if (qs <= ss && se <= qe) return tree[si];      // segment completely inside the query
                int mid = (ss + se) / 2;                         // partial overlap: ask both children
                return getSumRec(tree, qs, qe, ss, mid, 2 * si + 1) + getSumRec(tree, qs, qe, mid + 1, se, 2 * si + 2);
            }

            static int getSum(int[] tree, int n, int qs, int qe) {
                if (qs < 0 || qe > n - 1 || qs > qe) throw new IllegalArgumentException("invalid range");
                return getSumRec(tree, qs, qe, 0, n - 1, 0);
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 30, 40};
                int n = arr.length, x = 1;
                while (x < n) x *= 2;
                int[] tree = new int[2 * x - 1];
                build(arr, tree, 0, n - 1, 0);
                StringBuilder sb = new StringBuilder("tree:");
                for (int v : tree) sb.append(' ').append(v);
                System.out.println(sb);
                int[][] queries = {{0, 2}, {1, 3}, {2, 2}};
                for (int[] q : queries) System.out.println("sum(" + q[0] + ", " + q[1] + "): " + getSum(tree, n, q[0], q[1]));
            }
        }
    ''', js='''
        function build(arr, tree, ss, se, si) {
            if (ss === se) return (tree[si] = arr[ss]);
            const mid = Math.floor((ss + se) / 2);
            return (tree[si] = build(arr, tree, ss, mid, 2 * si + 1) + build(arr, tree, mid + 1, se, 2 * si + 2));
        }

        function getSumRec(tree, qs, qe, ss, se, si) {
            if (qe < ss || qs > se) return 0;                   // segment completely outside the query
            if (qs <= ss && se <= qe) return tree[si];          // segment completely inside the query
            const mid = Math.floor((ss + se) / 2);               // partial overlap: ask both children
            return getSumRec(tree, qs, qe, ss, mid, 2 * si + 1) + getSumRec(tree, qs, qe, mid + 1, se, 2 * si + 2);
        }

        function getSum(tree, n, qs, qe) {
            if (qs < 0 || qe > n - 1 || qs > qe) throw new Error("invalid range");
            return getSumRec(tree, qs, qe, 0, n - 1, 0);
        }

        const arr = [10, 20, 30, 40];
        const n = arr.length;
        let x = 1;
        while (x < n) x *= 2;
        const tree = new Array(2 * x - 1).fill(0);
        build(arr, tree, 0, n - 1, 0);
        console.log("tree:", tree.join(" "));
        for (const [qs, qe] of [[0, 2], [1, 3], [2, 2]]) console.log(`sum(${qs}, ${qe}):`, getSum(tree, n, qs, qe));
    ''')
    yield complexity("O(log n) per query", "O(log n) recursion depth")
    yield pitfall("The order of the two base cases matters: test *completely outside* before *completely inside*. For a single-element segment both `qe < ss` and `qs <= ss && se <= qe` can be evaluated — the outside test must win when the leaf is not in the range.")

    yield section("Point update", "pencil")
    yield io("arr = [10, 20, 30, 40]; update(1, 60); getSum(0, 2)", "100  (the tree becomes 140 70 70 10 60 30 40)")
    yield idea("Only the nodes whose segment **contains index `i`** — one per level, root to leaf — are affected. Compute `diff = newValue − arr[i]`, then walk down from the root adding `diff` to every node on the path to leaf `i` and ignoring the subtrees that do not contain `i`.")
    yield steps(
        ("Compute the difference", "`diff = new_val − arr[i]`; also store `arr[i] = new_val` so later updates compute the right difference."),
        ("`update(ss, se, i, si, diff)`", "If `i` is outside `[ss, se]` → return (this subtree is untouched)."),
        ("Add and descend", "`tree[si] += diff`; if the segment has more than one element, recurse into both children (only the one containing `i` does any work)."),
    )
    yield diagram('''
        update(1, 60) on [10, 20, 30, 40]: diff = 60 − 20 = +40

                 [0..3] 100 → 140            ← contains index 1: += 40
                /            \\
          [0..1] 30 → 70      [2..3] 70       ← index 1 not in [2..3]: skip
          /       \\
        [0] 10    [1] 20 → 60                 ← the leaf itself
    ''', "Exactly one node per level changes")
    yield multi('''
        tree: 100 30 70 10 20 30 40
        sum(0, 2): 60
        update(1, 60)
        tree: 140 70 70 10 60 30 40
        sum(0, 2): 100
        sum(1, 3): 130
    ''', py='''
        class SegmentTree:
            def __init__(self, arr):
                self.arr = arr[:]
                self.n = len(arr)
                x = 1
                while x < self.n:
                    x *= 2
                self.tree = [0] * (2 * x - 1)
                self._build(0, self.n - 1, 0)

            def _build(self, ss, se, si):
                if ss == se:
                    self.tree[si] = self.arr[ss]
                    return self.tree[si]
                mid = (ss + se) // 2
                self.tree[si] = self._build(ss, mid, 2 * si + 1) + self._build(mid + 1, se, 2 * si + 2)
                return self.tree[si]

            def get_sum(self, qs, qe, ss=0, se=None, si=0):
                if se is None:
                    se = self.n - 1
                if qe < ss or qs > se:
                    return 0
                if qs <= ss and se <= qe:
                    return self.tree[si]
                mid = (ss + se) // 2
                return self.get_sum(qs, qe, ss, mid, 2 * si + 1) + self.get_sum(qs, qe, mid + 1, se, 2 * si + 2)

            def update(self, i, new_val):
                diff = new_val - self.arr[i]                    # how much every ancestor must change
                self.arr[i] = new_val
                self._update(0, self.n - 1, i, 0, diff)

            def _update(self, ss, se, i, si, diff):
                if i < ss or i > se:                            # index not in this segment
                    return
                self.tree[si] += diff                           # this node's segment contains i
                if ss < se:
                    mid = (ss + se) // 2
                    self._update(ss, mid, i, 2 * si + 1, diff)
                    self._update(mid + 1, se, i, 2 * si + 2, diff)

        st = SegmentTree([10, 20, 30, 40])
        print("tree:", " ".join(map(str, st.tree)))
        print("sum(0, 2):", st.get_sum(0, 2))
        print("update(1, 60)")
        st.update(1, 60)
        print("tree:", " ".join(map(str, st.tree)))
        print("sum(0, 2):", st.get_sum(0, 2))
        print("sum(1, 3):", st.get_sum(1, 3))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        class SegmentTree {
            vector<int> arr, tree;
            int n;
            int build(int ss, int se, int si) {
                if (ss == se) return tree[si] = arr[ss];
                int mid = (ss + se) / 2;
                return tree[si] = build(ss, mid, 2 * si + 1) + build(mid + 1, se, 2 * si + 2);
            }
            int getSum(int qs, int qe, int ss, int se, int si) const {
                if (qe < ss || qs > se) return 0;
                if (qs <= ss && se <= qe) return tree[si];
                int mid = (ss + se) / 2;
                return getSum(qs, qe, ss, mid, 2 * si + 1) + getSum(qs, qe, mid + 1, se, 2 * si + 2);
            }
            void update(int ss, int se, int i, int si, int diff) {
                if (i < ss || i > se) return;                   // index not in this segment
                tree[si] += diff;                               // this node's segment contains i
                if (ss < se) {
                    int mid = (ss + se) / 2;
                    update(ss, mid, i, 2 * si + 1, diff);
                    update(mid + 1, se, i, 2 * si + 2, diff);
                }
            }
        public:
            SegmentTree(const vector<int>& a) : arr(a), n(a.size()) {
                int x = 1;
                while (x < n) x *= 2;
                tree.assign(2 * x - 1, 0);
                build(0, n - 1, 0);
            }
            int getSum(int qs, int qe) const { return getSum(qs, qe, 0, n - 1, 0); }
            void update(int i, int newVal) {
                int diff = newVal - arr[i];                     // how much every ancestor must change
                arr[i] = newVal;
                update(0, n - 1, i, 0, diff);
            }
            void print() const { cout << "tree:"; for (int v : tree) cout << " " << v; cout << "\\n"; }
        };

        int main() {
            SegmentTree st({10, 20, 30, 40});
            st.print();
            cout << "sum(0, 2): " << st.getSum(0, 2) << "\\n";
            cout << "update(1, 60)\\n";
            st.update(1, 60);
            st.print();
            cout << "sum(0, 2): " << st.getSum(0, 2) << "\\n";
            cout << "sum(1, 3): " << st.getSum(1, 3) << "\\n";
        }
    ''', java='''
        public class Main {
            static class SegmentTree {
                int[] arr, tree;
                int n;
                SegmentTree(int[] a) {
                    arr = a.clone(); n = a.length;
                    int x = 1;
                    while (x < n) x *= 2;
                    tree = new int[2 * x - 1];
                    build(0, n - 1, 0);
                }
                int build(int ss, int se, int si) {
                    if (ss == se) return tree[si] = arr[ss];
                    int mid = (ss + se) / 2;
                    return tree[si] = build(ss, mid, 2 * si + 1) + build(mid + 1, se, 2 * si + 2);
                }
                int getSum(int qs, int qe) { return getSum(qs, qe, 0, n - 1, 0); }
                int getSum(int qs, int qe, int ss, int se, int si) {
                    if (qe < ss || qs > se) return 0;
                    if (qs <= ss && se <= qe) return tree[si];
                    int mid = (ss + se) / 2;
                    return getSum(qs, qe, ss, mid, 2 * si + 1) + getSum(qs, qe, mid + 1, se, 2 * si + 2);
                }
                void update(int i, int newVal) {
                    int diff = newVal - arr[i];                 // how much every ancestor must change
                    arr[i] = newVal;
                    update(0, n - 1, i, 0, diff);
                }
                void update(int ss, int se, int i, int si, int diff) {
                    if (i < ss || i > se) return;               // index not in this segment
                    tree[si] += diff;                           // this node's segment contains i
                    if (ss < se) {
                        int mid = (ss + se) / 2;
                        update(ss, mid, i, 2 * si + 1, diff);
                        update(mid + 1, se, i, 2 * si + 2, diff);
                    }
                }
                String dump() { StringBuilder sb = new StringBuilder("tree:"); for (int v : tree) sb.append(' ').append(v); return sb.toString(); }
            }

            public static void main(String[] args) {
                SegmentTree st = new SegmentTree(new int[]{10, 20, 30, 40});
                System.out.println(st.dump());
                System.out.println("sum(0, 2): " + st.getSum(0, 2));
                System.out.println("update(1, 60)");
                st.update(1, 60);
                System.out.println(st.dump());
                System.out.println("sum(0, 2): " + st.getSum(0, 2));
                System.out.println("sum(1, 3): " + st.getSum(1, 3));
            }
        }
    ''', js='''
        class SegmentTree {
            constructor(a) {
                this.arr = [...a]; this.n = a.length;
                let x = 1;
                while (x < this.n) x *= 2;
                this.tree = new Array(2 * x - 1).fill(0);
                this.build(0, this.n - 1, 0);
            }
            build(ss, se, si) {
                if (ss === se) return (this.tree[si] = this.arr[ss]);
                const mid = Math.floor((ss + se) / 2);
                return (this.tree[si] = this.build(ss, mid, 2 * si + 1) + this.build(mid + 1, se, 2 * si + 2));
            }
            getSum(qs, qe, ss = 0, se = this.n - 1, si = 0) {
                if (qe < ss || qs > se) return 0;
                if (qs <= ss && se <= qe) return this.tree[si];
                const mid = Math.floor((ss + se) / 2);
                return this.getSum(qs, qe, ss, mid, 2 * si + 1) + this.getSum(qs, qe, mid + 1, se, 2 * si + 2);
            }
            update(i, newVal) {
                const diff = newVal - this.arr[i];              // how much every ancestor must change
                this.arr[i] = newVal;
                this.updateRec(0, this.n - 1, i, 0, diff);
            }
            updateRec(ss, se, i, si, diff) {
                if (i < ss || i > se) return;                   // index not in this segment
                this.tree[si] += diff;                          // this node's segment contains i
                if (ss < se) {
                    const mid = Math.floor((ss + se) / 2);
                    this.updateRec(ss, mid, i, 2 * si + 1, diff);
                    this.updateRec(mid + 1, se, i, 2 * si + 2, diff);
                }
            }
        }

        const st = new SegmentTree([10, 20, 30, 40]);
        console.log("tree:", st.tree.join(" "));
        console.log("sum(0, 2):", st.getSum(0, 2));
        console.log("update(1, 60)");
        st.update(1, 60);
        console.log("tree:", st.tree.join(" "));
        console.log("sum(0, 2):", st.getSum(0, 2));
        console.log("sum(1, 3):", st.getSum(1, 3));
    ''')
    yield complexity("O(log n) per update", "O(log n) recursion depth")
    yield note("For aggregates where a *difference* makes no sense (min, max, gcd) do not propagate `diff`; instead descend to the leaf, overwrite it, and on the way back up recompute each ancestor as `combine(tree[2si+1], tree[2si+2])`. That version works for every aggregate, including sum.", "Min / max trees")
    yield pitfall("Forgetting to write `arr[i] = new_val` makes the *second* update of the same index compute a wrong `diff` — the tree then silently drifts away from the array.")

    yield section("Interview Q&A", "message-question")
    yield qa("Segment tree vs binary indexed tree — which one and why?",
             "Both give `O(log n)` point update and range query over a fixed-size array. A BIT is shorter to code and uses `n + 1` slots, but only works for **invertible** operations (sum, XOR) where `prefix(r) − prefix(l−1)` makes sense. A segment tree handles any associative operation (min, max, gcd), range updates with lazy propagation, and is easier to extend — at the cost of `≈ 4n` memory and more code.")
    yield qa("Why is a range query O(log n) when it may recurse into both children?",
             "At every level at most **two** nodes are *partially* overlapped by the query (the ones containing its left and right boundaries); every other visited node is either fully inside or fully outside and returns immediately. So the recursion touches at most `4` nodes per level × `log n` levels.")
    yield qa("How much memory does a segment tree need and why 4n?",
             "Exactly `2n − 1` nodes when `n` is a power of two; otherwise at most `2x − 1` where `x` is the next power of two above `n`. Since `x < 2n`, `2x − 1 < 4n`, which is why `4n` is the usual safe allocation. The iterative *bottom-up* segment tree needs only `2n`.")
    yield qa("How would you support range updates (add v to every element in [l, r])?",
             "With **lazy propagation**: store a pending `add` value in each node; a range update marks the fully covered nodes lazily instead of descending to every leaf, and the pending value is pushed down to the children only when a later query or update needs to look inside. Both operations stay `O(log n)`.")
    yield qa("Can a segment tree be built for an array that grows?",
             "Not directly — the structure assumes a fixed size. Either allocate for the maximum size up front (unused leaves hold the identity element, `0` for sums), or use a dynamic / implicit segment tree that creates nodes on demand.")


@topic(G, "binary_indexed_tree", "Binary Indexed Tree", "chart-histogram")
def _():
    yield lead("A binary indexed tree (Fenwick tree) supports **prefix queries** and **point updates** over a fixed-size array in `O(log n)` each, using a single array of `n + 1` integers and a handful of lines of code. It is the lightweight alternative to a segment tree for sums, counts and XORs.")
    yield define("Binary indexed tree (BIT, Fenwick tree)", "an array `BIT[1..n]` in which `BIT[i]` stores the sum of the `i & −i` elements of the input ending at position `i` (1-based). Prefix sums and updates both walk `O(log n)` entries by repeatedly clearing or adding the lowest set bit of the index.")
    yield p("It is used for a fixed input array with many operations of two kinds: a **prefix operation** — sum, product, XOR, OR, count — and **updating a value**. It is stored as a plain array, but the idea behind the indices is a tree. It needs `O(n log n)` preprocessing (`O(n)` with a trick) and `Θ(n)` auxiliary space.")
    yield io("arr = [10, 20, 30, 40, 50, 60]; getSum(2); getSum(4)", "60 150", "update(2, 35); getSum(2); getSum(4)", "65 155")
    yield formula("rangeSum(i, j) = prefixSum(j) − prefixSum(i − 1)")

    yield section("Three approaches to prefix sum + update", "scale")
    yield p("`getSum(i)` returns `arr[0] + … + arr[i]`; `update(i, x)` sets `arr[i] = x`. Both operations are frequent and interleaved.")
    yield table(
        ["Method", "`getSum(i)`", "`update(i, x)`", "Space", "Code"],
        ["**1 — simple**: loop from `0` to `i`", "O(n)", "O(1) — `arr[i] = x`", "O(1)", "trivial"],
        ["**2 — prefix-sum array**: `pre[i]`", "O(1)", "O(n) — add `diff` to `pre[i..n−1]`", "O(n)", "trivial"],
        ["**3 — segment tree**", "O(log n)", "O(log n)", "≈ 4n", "three recursive functions"],
        ["**Binary indexed tree**", "O(log n)", "O(log n)", "n + 1", "**two short loops**"],
    )
    yield p("Methods 1 and 2 each make one operation linear; with a mixed workload the average cost is `O(n)` per operation. The segment tree fixes that but is a comparatively heavy piece of code. The BIT gets the same `O(log n)` for both operations with less memory and about ten lines.")
    yield note("Unlike a segment tree, a BIT works only for operations that have an **inverse**: `rangeSum(i, j) = getSum(j) − getSum(i−1)` needs subtraction. Prefix *min* or *max* cannot be undone, so range-min queries need a segment tree.", "Limitation")

    yield section("The idea: every prefix is a sum of powers of two", "binary")
    yield p("Any positive integer is a sum of distinct powers of two: `14 = 8 + 4 + 2`. So a prefix of length `14` can be split into three blocks of lengths `8`, `4` and `2`, and if the sum of each block is pre-computed, `getSum` needs three additions instead of fourteen. The BIT stores exactly these blocks: entry `i` (1-based) is responsible for the **last `i & −i` elements ending at `i`**.")
    yield diagram('''
        arr (0-based):  10   20   30   40   50   60
        BIT index i  :   1    2    3    4    5    6
        i & -i       :   1    2    1    4    1    2
        covers       :  [1] [1,2] [3] [1..4] [5] [5,6]
        BIT[i]       :  10   30   30   100   50  110

                      0 (virtual root)
                ┌─────┼──────────┐
                1     2          4           parent of i for queries = i − (i & −i)
                      │        ┌─┴─┐
                      3        5   6

        getSum(4) → arr[0..4] → i = 5:  BIT[5] + BIT[4] = 50 + 100 = 150
    ''', "Each BIT entry covers a block whose length is the lowest set bit of its index; a query adds up the blocks on the path to the root")

    yield section("The i & -i trick: isolating the lowest set bit", "binary")
    yield p("`−i` in two's complement is `~i + 1`: flip every bit, then add one. Flipping turns the trailing zeros of `i` into ones and the lowest `1` into `0`; adding one carries through those ones and stops exactly at that position. The result shares only that one bit with `i`, so `i & −i` is the lowest set bit as a power of two.")
    yield diagram('''
         i = 6  :  0 1 1 0
        ~i      :  1 0 0 1
        -i = ~i+1: 1 0 1 0
         i & -i :  0 0 1 0   = 2        6 → block of length 2 ([5, 6]);  6 − 2 = 4 is the next block

         i = 12 :  1 1 0 0
        -i      :  0 1 0 0
         i & -i :  0 1 0 0   = 4        12 → block of length 4 ([9..12]); 12 − 4 = 8 is the next block
    ''', "i & −i for i = 6 and i = 12")
    yield snippet("py", '''
        for i in range(1, 9):
            print(f"{i}  {i:04b}  lowest set bit = {i & -i}")
    ''', out='''
         1  0001  lowest set bit = 1
         2  0010  lowest set bit = 2
         3  0011  lowest set bit = 1
         4  0100  lowest set bit = 4
         5  0101  lowest set bit = 1
         6  0110  lowest set bit = 2
         7  0111  lowest set bit = 1
         8  1000  lowest set bit = 8
    ''')
    yield table(
        ["Expression", "Effect", "Used by"],
        ["`i -= i & -i`", "clear the lowest set bit → jump to the parent block", "`getSum` (walk towards 0)"],
        ["`i += i & -i`", "add the lowest set bit → jump to the next entry whose block contains `i`", "`update` (walk towards n)"],
    )

    yield section("getSum: prefix sum", "sum")
    yield p("To get the sum of `arr[0..i]`, convert to the 1-based BIT index `i + 1` and keep adding `BIT[i]` while clearing the lowest set bit. Every step removes one `1` bit, so there are at most `log₂ n` steps.")
    yield diagram('''
        getSum(i):
            i = i + 1                     # BIT is 1-based
            result = 0
            while i > 0:
                result += BIT[i]
                i -= i & -i               # parent(i): drop the lowest set bit
            return result

        result = BIT[i] + BIT[parent(i)] + BIT[parent(parent(i))] + …
    ''', "Prefix sum walks from i towards 0")
    yield example("`getSum(4)`: `i = 5 (101)` → add `BIT[5] = 50`, `i = 4 (100)` → add `BIT[4] = 100`, `i = 0` → stop. Result `150`.")

    yield section("update: change one value", "pencil")
    yield p("The first parameter is an index of `arr`. Compute `diff = x − arr[i]`, store the new value, convert to the 1-based index and add `diff` to every BIT entry whose block contains `i` — these are reached by **adding** the lowest set bit each time until the index exceeds `n`.")
    yield diagram('''
        update(i, x):
            diff = x - arr[i]
            arr[i] = x
            i = i + 1
            while i <= n:
                BIT[i] += diff
                i += i & -i               # next entry whose block includes position i

        update(2, 35) with n = 6: diff = +5
            i = 3 (011) → BIT[3] += 5        covers [3]
            i = 4 (100) → BIT[4] += 5        covers [1..4]
            i = 8        > 6 → stop          (BIT[5], BIT[6] cover [5], [5,6] — unaffected)
    ''', "Update walks from i towards n")

    yield section("Construction and the complete program", "hammer")
    yield idea("Build the BIT by starting from all zeros and calling `update(i, arr[i])` for every element — `n` updates of `O(log n)` each. The program below builds the tree for `[10, 20, 30, 40, 50, 60]`, answers prefix and range sums, performs an update and queries again.")
    yield multi('''
        BIT: 10 30 30 100 50 110
        getSum(2): 60
        getSum(4): 150
        rangeSum(1, 4): 140
        update(2, 35)
        BIT: 10 30 35 105 50 110
        getSum(2): 65
        getSum(4): 155
    ''', py='''
        class FenwickTree:
            def __init__(self, arr):
                self.n = len(arr)
                self.arr = [0] * self.n                  # current values, needed to compute diff
                self.bit = [0] * (self.n + 1)            # 1-based
                for i, v in enumerate(arr):
                    self.update(i, v)                    # construction = n updates

            def get_sum(self, i):                        # sum of arr[0..i]
                i += 1
                res = 0
                while i > 0:
                    res += self.bit[i]
                    i -= i & -i                          # drop the lowest set bit → parent block
                return res

            def range_sum(self, l, r):
                return self.get_sum(r) - (self.get_sum(l - 1) if l > 0 else 0)

            def update(self, i, x):                      # set arr[i] = x
                diff = x - self.arr[i]
                self.arr[i] = x
                i += 1
                while i <= self.n:
                    self.bit[i] += diff
                    i += i & -i                          # next block that contains position i

        ft = FenwickTree([10, 20, 30, 40, 50, 60])
        print("BIT:", " ".join(map(str, ft.bit[1:])))
        print("getSum(2):", ft.get_sum(2))
        print("getSum(4):", ft.get_sum(4))
        print("rangeSum(1, 4):", ft.range_sum(1, 4))
        print("update(2, 35)")
        ft.update(2, 35)
        print("BIT:", " ".join(map(str, ft.bit[1:])))
        print("getSum(2):", ft.get_sum(2))
        print("getSum(4):", ft.get_sum(4))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        class FenwickTree {
            int n;
            vector<int> arr, bit;                        // arr = current values, bit = 1-based tree
        public:
            FenwickTree(const vector<int>& a) : n(a.size()), arr(n, 0), bit(n + 1, 0) {
                for (int i = 0; i < n; i++) update(i, a[i]);   // construction = n updates
            }
            int getSum(int i) const {                    // sum of arr[0..i]
                int res = 0;
                for (i = i + 1; i > 0; i -= i & -i)      // drop the lowest set bit → parent block
                    res += bit[i];
                return res;
            }
            int rangeSum(int l, int r) const { return getSum(r) - (l > 0 ? getSum(l - 1) : 0); }
            void update(int i, int x) {                  // set arr[i] = x
                int diff = x - arr[i];
                arr[i] = x;
                for (i = i + 1; i <= n; i += i & -i)     // next block that contains position i
                    bit[i] += diff;
            }
            void print() const { cout << "BIT:"; for (int i = 1; i <= n; i++) cout << " " << bit[i]; cout << "\\n"; }
        };

        int main() {
            FenwickTree ft({10, 20, 30, 40, 50, 60});
            ft.print();
            cout << "getSum(2): " << ft.getSum(2) << "\\n";
            cout << "getSum(4): " << ft.getSum(4) << "\\n";
            cout << "rangeSum(1, 4): " << ft.rangeSum(1, 4) << "\\n";
            cout << "update(2, 35)\\n";
            ft.update(2, 35);
            ft.print();
            cout << "getSum(2): " << ft.getSum(2) << "\\n";
            cout << "getSum(4): " << ft.getSum(4) << "\\n";
        }
    ''', java='''
        public class Main {
            static class FenwickTree {
                int n;
                int[] arr, bit;                          // arr = current values, bit = 1-based tree
                FenwickTree(int[] a) {
                    n = a.length; arr = new int[n]; bit = new int[n + 1];
                    for (int i = 0; i < n; i++) update(i, a[i]);   // construction = n updates
                }
                int getSum(int i) {                      // sum of arr[0..i]
                    int res = 0;
                    for (i = i + 1; i > 0; i -= i & -i)  // drop the lowest set bit → parent block
                        res += bit[i];
                    return res;
                }
                int rangeSum(int l, int r) { return getSum(r) - (l > 0 ? getSum(l - 1) : 0); }
                void update(int i, int x) {              // set arr[i] = x
                    int diff = x - arr[i];
                    arr[i] = x;
                    for (i = i + 1; i <= n; i += i & -i) // next block that contains position i
                        bit[i] += diff;
                }
                String dump() { StringBuilder sb = new StringBuilder("BIT:"); for (int i = 1; i <= n; i++) sb.append(' ').append(bit[i]); return sb.toString(); }
            }

            public static void main(String[] args) {
                FenwickTree ft = new FenwickTree(new int[]{10, 20, 30, 40, 50, 60});
                System.out.println(ft.dump());
                System.out.println("getSum(2): " + ft.getSum(2));
                System.out.println("getSum(4): " + ft.getSum(4));
                System.out.println("rangeSum(1, 4): " + ft.rangeSum(1, 4));
                System.out.println("update(2, 35)");
                ft.update(2, 35);
                System.out.println(ft.dump());
                System.out.println("getSum(2): " + ft.getSum(2));
                System.out.println("getSum(4): " + ft.getSum(4));
            }
        }
    ''', js='''
        class FenwickTree {
            constructor(a) {
                this.n = a.length;
                this.arr = new Array(this.n).fill(0);        // current values, needed to compute diff
                this.bit = new Array(this.n + 1).fill(0);    // 1-based
                a.forEach((v, i) => this.update(i, v));      // construction = n updates
            }
            getSum(i) {                                      // sum of arr[0..i]
                let res = 0;
                for (i = i + 1; i > 0; i -= i & -i) res += this.bit[i];   // drop the lowest set bit → parent block
                return res;
            }
            rangeSum(l, r) { return this.getSum(r) - (l > 0 ? this.getSum(l - 1) : 0); }
            update(i, x) {                                   // set arr[i] = x
                const diff = x - this.arr[i];
                this.arr[i] = x;
                for (i = i + 1; i <= this.n; i += i & -i) this.bit[i] += diff;   // next block that contains position i
            }
        }

        const ft = new FenwickTree([10, 20, 30, 40, 50, 60]);
        console.log("BIT:", ft.bit.slice(1).join(" "));
        console.log("getSum(2):", ft.getSum(2));
        console.log("getSum(4):", ft.getSum(4));
        console.log("rangeSum(1, 4):", ft.rangeSum(1, 4));
        console.log("update(2, 35)");
        ft.update(2, 35);
        console.log("BIT:", ft.bit.slice(1).join(" "));
        console.log("getSum(2):", ft.getSum(2));
        console.log("getSum(4):", ft.getSum(4));
    ''')
    yield complexity("O(log n) per getSum / update; O(n log n) construction", "O(n)")
    yield note("Construction can be `O(n)`: copy `arr` into `BIT[1..n]`, then for `i = 1..n` add `BIT[i]` into `BIT[i + (i & −i)]` if that index is `≤ n`. Every entry pushes its total to the one parent block that contains it — one pass, no logarithm.", "Linear construction")
    yield pitfall("Two off-by-one traps: the BIT is **1-based** (so `arr[i]` lives at `i + 1`, and `BIT[0]` is never used), and `update` must use the **difference** against the stored `arr[i]`, not the new value — unless you are *adding* to an element rather than *setting* it, in which case the diff is the amount added and no `arr` copy is needed.")

    yield section("Interview Q&A", "message-question")
    yield qa("Explain i & -i.",
             "In two's complement `−i = ~i + 1`. Negating flips all bits, and the `+1` carries through the trailing ones, stopping at the position of `i`'s lowest set bit. That bit is the only one set in both `i` and `−i`, so `i & −i` is exactly the lowest set bit (a power of two). In a BIT it is the length of the block entry `i` is responsible for.")
    yield qa("Why is getSum O(log n)?",
             "Every iteration clears one set bit of the index (`i -= i & -i`). A number below `n` has at most `⌊log₂ n⌋ + 1` set bits, so the loop runs that many times at most. `update` is symmetric: `i += i & -i` increases the position of the lowest set bit each time, so it also takes `O(log n)` steps to exceed `n`.")
    yield qa("BIT vs segment tree?",
             "Same `O(log n)` for point update and prefix/range query. BIT: `n + 1` memory, ~10 lines, faster constants; but only for **invertible** operations (sum, XOR, count) and point updates. Segment tree: any associative operation (min, max, gcd), range updates via lazy propagation, ≈ `4n` memory, more code.")
    yield qa("How do you do a range update + point query with a BIT?",
             "Store the **differences**: to add `v` to `[l, r]` do `add(l, v)` and `add(r + 1, −v)`; a point query at `i` is then `prefixSum(i)`. Range update + range query needs two BITs. Both tricks rely on the sum being invertible.")
    yield qa("Name two classic BIT applications beyond prefix sums.",
             "**Counting inversions** in `O(n log n)`: scan left to right and query how many previously seen values are greater. **Order statistics / k-th smallest** among the inserted values with a binary search over the BIT (`O(log² n)` or `O(log n)` with bit-walking). Both treat the BIT as a dynamic frequency table.")
