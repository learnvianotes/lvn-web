class Solution {
public:
    int numDecodings(string s) {
        return dfs(s, 0);
    }

private:
    int dfs(const string& s, int i) {
        if (i == (int)s.size()) return 1;
        if (s[i] == '0') return 0;

        int result = dfs(s, i + 1);

        if (i + 1 < (int)s.size()) {
            int twoDigit = stoi(s.substr(i, 2));
            if (twoDigit >= 10 && twoDigit <= 26) {
                result += dfs(s, i + 2);
            }
        }

        return result;
    }
};
