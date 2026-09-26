class Solution {
public:
    bool isMatch(string s, string p) {
        // memo[i][j]: -1 = not computed, 0 = false, 1 = true
        memo.assign(s.size() + 1, vector<int>(p.size() + 1, -1));
        return dfs(s, p, 0, 0);
    }

private:
    vector<vector<int>> memo;

    bool dfs(const string& s, const string& p, int i, int j) {
        if (memo[i][j] != -1) return memo[i][j];

        if (j == (int)p.size()) return i == (int)s.size();

        bool firstMatch = i < (int)s.size() && (p[j] == s[i] || p[j] == '.');
        bool answer;

        if (j + 1 < (int)p.size() && p[j + 1] == '*') {
            answer = dfs(s, p, i, j + 2) || (firstMatch && dfs(s, p, i + 1, j));
        } else {
            answer = firstMatch && dfs(s, p, i + 1, j + 1);
        }

        memo[i][j] = answer;
        return answer;
    }
};
