class Solution {
public:
    vector<vector<string>> partition(string s) {
        vector<vector<string>> result;
        vector<string> current;
        backtrack(s, 0, current, result);
        return result;
    }

private:
    bool isPalindrome(const string& str) {
        return str == string(str.rbegin(), str.rend());
    }

    void backtrack(const string& s, int start, vector<string>& current, vector<vector<string>>& result) {
        if (start == (int)s.size()) {
            result.push_back(current);
            return;
        }

        for (int end = start + 1; end <= (int)s.size(); end++) {
            string substring = s.substr(start, end - start);

            if (isPalindrome(substring)) {
                current.push_back(substring);
                backtrack(s, end, current, result);
                current.pop_back();
            }
        }
    }
};
