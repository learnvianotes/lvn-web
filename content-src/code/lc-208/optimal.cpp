struct TrieNode {
    unordered_map<char, TrieNode*> children;
    bool isWord = false;
};

class Trie {
public:
    Trie() : root(new TrieNode()) {}

    void insert(string word) {
        TrieNode* node = root;

        for (char c : word) {
            if (!node->children.count(c)) node->children[c] = new TrieNode();

            node = node->children[c];
        }

        node->isWord = true;
    }

    bool search(string word) {
        TrieNode* node = root;

        for (char c : word) {
            if (!node->children.count(c)) return false;

            node = node->children[c];
        }

        return node->isWord;
    }

    bool startsWith(string prefix) {
        TrieNode* node = root;

        for (char c : prefix) {
            if (!node->children.count(c)) return false;

            node = node->children[c];
        }

        return true;
    }

private:
    TrieNode* root;
};
