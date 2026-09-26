class Solution {
public:
    int characterReplacement(string s, int k) {
        unordered_map<char, int> count;
        int left = 0, maxFrequency = 0, answer = 0;
        for (int right = 0; right < s.size(); right++) {
            count[s[right]]++;
            maxFrequency = max(maxFrequency, count[s[right]]);
            while (right - left + 1 - maxFrequency > k) {
                count[s[left]]--;
                left++;
            }
            answer = max(answer, right - left + 1);
        }
        return answer;
    }
};
