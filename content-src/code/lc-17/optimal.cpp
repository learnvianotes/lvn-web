class Solution {
    const vector<string> phone = {
        "", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
    };

public:
    vector<string> letterCombinations(string digits) {
        if (digits.empty()) return {};

        vector<string> result;
        string current;
        backtrack(digits, 0, current, result);
        return result;
    }

private:
    void backtrack(const string& digits, int index, string& current, vector<string>& result) {
        if (index == (int)digits.size()) {
            result.push_back(current);
            return;
        }

        const string& letters = phone[digits[index] - '0'];

        for (char ch : letters) {
            current.push_back(ch);
            backtrack(digits, index + 1, current, result);
            current.pop_back();
        }
    }
};
