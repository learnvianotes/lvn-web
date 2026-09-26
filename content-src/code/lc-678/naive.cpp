class Solution {
public:
    bool checkValidString(string s) {
        return dfs(s, 0, 0);
    }

private:
    bool dfs(const string& s, int index, int balance) {
        if (balance < 0) {
            return false;
        }

        if (index == (int)s.size()) {
            return balance == 0;
        }

        char c = s[index];

        if (c == '(') {
            return dfs(s, index + 1, balance + 1);
        }

        if (c == ')') {
            return dfs(s, index + 1, balance - 1);
        }

        // Try '*' as '(', ')', or ''
        return dfs(s, index + 1, balance + 1)
            || dfs(s, index + 1, balance - 1)
            || dfs(s, index + 1, balance);
    }
};
