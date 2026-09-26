class Solution {
    public String minWindow(String s, String t) {
        if (t.isEmpty()) return "";
        Map<Character, Integer> need = new HashMap<>(), have = new HashMap<>();
        for (char c : t.toCharArray()) need.put(c, need.getOrDefault(c, 0) + 1);
        int required = need.size(), formed = 0;
        int left = 0, bestLength = Integer.MAX_VALUE, bestStart = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            have.put(c, have.getOrDefault(c, 0) + 1);
            if (need.containsKey(c) && have.get(c).equals(need.get(c))) formed++;
            while (formed == required) {
                if (right - left + 1 < bestLength) {
                    bestLength = right - left + 1;
                    bestStart = left;
                }
                char leftChar = s.charAt(left);
                have.put(leftChar, have.get(leftChar) - 1);
                if (need.containsKey(leftChar) && have.get(leftChar) < need.get(leftChar)) formed--;
                left++;
            }
        }
        if (bestLength == Integer.MAX_VALUE) return "";
        return s.substring(bestStart, bestStart + bestLength);
    }
}
