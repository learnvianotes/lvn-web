class Solution {
public:
    vector<vector<string>> partition(string s) {
        int n = s.size();

        vector<vector<bool>> palindrome(n, vector<bool>(n, false));

        for (int i = 0; i < n; i++) palindrome[i][i] = true;

        for (int length = 2; length <= n; length++) {
            for (int left = 0; left <= n - length; left++) {
                int right = left + length - 1;

                if (s[left] == s[right]) {
                    if (length == 2 || palindrome[left + 1][right - 1]) {
                        palindrome[left][right] = true;
                    }
                }
            }
        }

        vector<vector<string>> result;
        vector<string> current;
        backtrack(s, 0, palindrome, current, result);
        return result;
    }

private:
    void backtrack(const string& s, int start, vector<vector<bool>>& palindrome,
                   vector<string>& current, vector<vector<string>>& result) {
        int n = s.size();

        if (start == n) {
            result.push_back(current);
            return;
        }

        for (int end = start; end < n; end++) {
            if (palindrome[start][end]) {
                current.push_back(s.substr(start, end - start + 1));
                backtrack(s, end + 1, palindrome, current, result);
                current.pop_back();
            }
        }
    }
};
