class Trie {
public:
    Trie() {}

    void insert(string word) {
        if (find(words.begin(), words.end(), word) == words.end()) {
            words.push_back(word);
        }
    }

    bool search(string word) {
        return find(words.begin(), words.end(), word) != words.end();
    }

    bool startsWith(string prefix) {
        for (const string& word : words) {
            if (word.compare(0, prefix.size(), prefix) == 0) return true;
        }

        return false;
    }

private:
    vector<string> words;
};
