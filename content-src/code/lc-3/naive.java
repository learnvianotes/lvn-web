class Solution {
    public int lengthOfLongestSubstring(String s) {
        int answer = 0;
        for (int i = 0; i < s.length(); i++) {
            Set<Character> seen = new HashSet<>();
            for (int j = i; j < s.length(); j++) {
                if (seen.contains(s.charAt(j))) break;
                seen.add(s.charAt(j));
                answer = Math.max(answer, j - i + 1);
            }
        }
        return answer;
    }
}
