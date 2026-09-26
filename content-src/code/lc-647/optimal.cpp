class Solution {
public:
    int countSubstrings(string s) {
        int count = 0;

        for (int i = 0; i < (int)s.size(); i++) {
            expand(s, i, i, count);
            expand(s, i, i + 1, count);
        }

        return count;
    }

private:
    void expand(const string& s, int left, int right, int& count) {
        while (left >= 0 && right < (int)s.size() && s[left] == s[right]) {
            count++;
            left--;
            right++;
        }
    }
};
