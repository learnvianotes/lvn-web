class Solution {
    public int characterReplacement(String s, int k) {
        Map<Character, Integer> count = new HashMap<>();
        int left = 0, maxFrequency = 0, answer = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            count.put(c, count.getOrDefault(c, 0) + 1);
            maxFrequency = Math.max(maxFrequency, count.get(c));
            while (right - left + 1 - maxFrequency > k) {
                count.put(s.charAt(left), count.get(s.charAt(left)) - 1);
                left++;
            }
            answer = Math.max(answer, right - left + 1);
        }
        return answer;
    }
}
