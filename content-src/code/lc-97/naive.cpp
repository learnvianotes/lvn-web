class Solution {
public:
    bool isInterleave(string s1, string s2, string s3) {
        if (s1.size() + s2.size() != s3.size()) return false;
        return dfs(s1, s2, s3, 0, 0);
    }

private:
    bool dfs(const string& s1, const string& s2, const string& s3, int i, int j) {
        int k = i + j;
        if (k == (int)s3.size()) return true;

        if (i < (int)s1.size() && s1[i] == s3[k]) {
            if (dfs(s1, s2, s3, i + 1, j)) return true;
        }

        if (j < (int)s2.size() && s2[j] == s3[k]) {
            if (dfs(s1, s2, s3, i, j + 1)) return true;
        }

        return false;
    }
};
