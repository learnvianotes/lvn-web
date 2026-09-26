class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        unordered_set<string> words(wordDict.begin(), wordDict.end());
        return dfs(s, words, 0);
    }

private:
    bool dfs(const string& s, unordered_set<string>& words, int start) {
        if (start == (int)s.size()) return true;

        for (int end = start + 1; end <= (int)s.size(); end++) {
            if (words.count(s.substr(start, end - start))) {
                if (dfs(s, words, end)) return true;
            }
        }

        return false;
    }
};
