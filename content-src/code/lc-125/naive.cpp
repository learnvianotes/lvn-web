class Solution {
public:
    bool isPalindrome(string s) {
        string cleaned;
        for (char c : s)
            if (isalnum((unsigned char)c)) cleaned += tolower((unsigned char)c);
        return cleaned == string(cleaned.rbegin(), cleaned.rend());
    }
};
