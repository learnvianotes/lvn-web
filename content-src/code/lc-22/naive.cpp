class Solution {
public:
    vector<string> generateParenthesis(int n) {
        vector<string> result;
        generate("", n, result);
        return result;
    }

private:
    bool valid(const string& s) {
        int balance = 0;
        for (char c : s) {
            if (c == '(') balance++;
            else balance--;
            if (balance < 0) return false;
        }
        return balance == 0;
    }

    void generate(const string& s, int n, vector<string>& result) {
        if (s.size() == 2 * n) {
            if (valid(s)) result.push_back(s);
            return;
        }
        generate(s + "(", n, result);
        generate(s + ")", n, result);
    }
};
