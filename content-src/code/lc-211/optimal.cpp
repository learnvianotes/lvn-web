struct TrieNode {
    unordered_map<char, TrieNode*> children;
    bool isWord = false;
};

class WordDictionary {
public:
    WordDictionary() : root(new TrieNode()) {}

    void addWord(string word) {
        TrieNode* node = root;

        for (char c : word) {
            if (!node->children.count(c)) node->children[c] = new TrieNode();

            node = node->children[c];
        }

        node->isWord = true;
    }

    bool search(string word) {
        return dfs(word, 0, root);
    }

private:
    TrieNode* root;

    bool dfs(const string& word, int index, TrieNode* node) {
        if (index == (int)word.size()) return node->isWord;

        char c = word[index];

        if (c != '.') {
            if (!node->children.count(c)) return false;

            return dfs(word, index + 1, node->children[c]);
        }

        // Wildcard: try all children
        for (auto& [_, child] : node->children) {
            if (dfs(word, index + 1, child)) return true;
        }

        return false;
    }
};
