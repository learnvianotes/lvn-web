class Solution {
    public int characterReplacement(String s, int k) {
        int answer = 0;
        for (int left = 0; left < s.length(); left++) {
            Map<Character, Integer> count = new HashMap<>();
            for (int right = left; right < s.length(); right++) {
                count.put(s.charAt(right), count.getOrDefault(s.charAt(right), 0) + 1);
                int length = right - left + 1;
                int mostFrequent = Collections.max(count.values());
                if (length - mostFrequent <= k) answer = Math.max(answer, length);
            }
        }
        return answer;
    }
}
