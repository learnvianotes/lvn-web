class Solution {
public:
    int numDistinct(string s, string t) {
        return dfs(s, t, 0, 0);
    }

private:
    int dfs(const string& s, const string& t, int i, int j) {
        if (j == (int)t.size()) return 1;
        if (i == (int)s.size()) return 0;

        if (s[i] == t[j]) {
            return dfs(s, t, i + 1, j + 1) + dfs(s, t, i + 1, j);
        }

        return dfs(s, t, i + 1, j);
    }
};
