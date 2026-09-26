class Solution {
public:
    int characterReplacement(string s, int k) {
        int answer = 0;
        for (int left = 0; left < s.size(); left++) {
            unordered_map<char, int> count;
            for (int right = left; right < s.size(); right++) {
                count[s[right]]++;
                int length = right - left + 1;
                int mostFrequent = 0;
                for (auto& [ch, c] : count) mostFrequent = max(mostFrequent, c);
                if (length - mostFrequent <= k) answer = max(answer, length);
            }
        }
        return answer;
    }
};
