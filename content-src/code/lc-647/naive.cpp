class Solution {
public:
    int countSubstrings(string s) {
        int count = 0;

        for (int i = 0; i < (int)s.size(); i++) {
            for (int j = i; j < (int)s.size(); j++) {
                if (isPalindrome(s, i, j)) count++;
            }
        }

        return count;
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
