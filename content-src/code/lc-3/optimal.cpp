class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        unordered_set<char> seen;
        int left = 0, answer = 0;
        for (int right = 0; right < s.size(); right++) {
            while (seen.count(s[right])) {
                seen.erase(s[left]);
                left++;
            }
            seen.insert(s[right]);
            answer = max(answer, right - left + 1);
        }
        return answer;
    }
};
