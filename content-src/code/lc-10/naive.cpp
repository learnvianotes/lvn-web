class Solution {
public:
    bool isMatch(string s, string p) {
        return dfs(s, p, 0, 0);
    }

private:
    bool dfs(const string& s, const string& p, int i, int j) {
        if (j == (int)p.size()) return i == (int)s.size();

        bool firstMatch = i < (int)s.size() && (p[j] == s[i] || p[j] == '.');

        if (j + 1 < (int)p.size() && p[j + 1] == '*') {
            return dfs(s, p, i, j + 2) || (firstMatch && dfs(s, p, i + 1, j));
        }

        return firstMatch && dfs(s, p, i + 1, j + 1);
    }
};
