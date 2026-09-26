class Solution {
public:
    string alienOrder(vector<string>& words) {
        string chars;
        for (auto& word : words)
            for (char c : word)
                if (chars.find(c) == string::npos) chars += c;

        sort(chars.begin(), chars.end());

        // Try every ordering of the letters
        do {
            if (isSorted(words, chars)) return chars;
        } while (next_permutation(chars.begin(), chars.end()));

        return "";
    }

private:
    // Are the words sorted under this alphabet order?
    bool isSorted(const vector<string>& words, const string& order) {
        int rank[26] = {};
        for (int i = 0; i < (int)order.size(); i++) rank[order[i] - 'a'] = i;

        for (int i = 0; i + 1 < (int)words.size(); i++) {
            const string& w1 = words[i];
            const string& w2 = words[i + 1];
            int j = 0;

            while (j < (int)w1.size() && j < (int)w2.size() && w1[j] == w2[j]) j++;

            if (j == (int)w1.size() || j == (int)w2.size()) {
                if (w1.size() > w2.size()) return false;  // longer word before its prefix
            } else if (rank[w1[j] - 'a'] > rank[w2[j] - 'a']) {
                return false;
            }
        }

        return true;
    }
};
