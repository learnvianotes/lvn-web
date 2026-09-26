class Solution {
public:
    string longestPalindrome(string s) {
        string longest = "";

        for (int i = 0; i < (int)s.size(); i++) {
            for (int j = i; j < (int)s.size(); j++) {
                if (isPalindrome(s, i, j) && j - i + 1 > (int)longest.size()) {
                    longest = s.substr(i, j - i + 1);
                }
            }
        }

        return longest;
    }

private:
    bool isPalindrome(const string& s, int left, int right) {
        while (left < right) {
            if (s[left] != s[right]) return false;
            left++;
            right--;
        }
        return true;
    }
};
