class Solution {
public:
    string minWindow(string s, string t) {
        if (t.empty()) return "";
        unordered_map<char, int> need, have;
        for (char c : t) need[c]++;
        int required = need.size(), formed = 0;
        int left = 0, bestLength = INT_MAX, bestStart = 0;
        for (int right = 0; right < s.size(); right++) {
            char c = s[right];
            have[c]++;
            if (need.count(c) && have[c] == need[c]) formed++;
            while (formed == required) {
                if (right - left + 1 < bestLength) {
                    bestLength = right - left + 1;
                    bestStart = left;
                }
                char leftChar = s[left];
                have[leftChar]--;
                if (need.count(leftChar) && have[leftChar] < need[leftChar]) formed--;
                left++;
            }
        }
        if (bestLength == INT_MAX) return "";
        return s.substr(bestStart, bestLength);
    }
};
