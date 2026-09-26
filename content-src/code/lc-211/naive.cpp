class WordDictionary {
public:
    WordDictionary() {}

    void addWord(string word) {
        words.push_back(word);
    }

    bool search(string word) {
        for (const string& candidate : words) {
            if (candidate.size() != word.size()) continue;

            bool match = true;

            for (int i = 0; i < (int)word.size(); i++) {
                if (word[i] != '.' && word[i] != candidate[i]) {
                    match = false;
                    break;
                }
            }

            if (match) return true;
        }

        return false;
    }

private:
    vector<string> words;
};
