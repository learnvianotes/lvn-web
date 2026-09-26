class Solution {
    public String minWindow(String s, String t) {
        if (t.isEmpty()) return "";
        String answer = "";
        for (int left = 0; left < s.length(); left++) {
            Map<Character, Integer> count = new HashMap<>();
            for (int right = left; right < s.length(); right++) {
                count.put(s.charAt(right), count.getOrDefault(s.charAt(right), 0) + 1);
                boolean valid = true;
                for (char c : t.toCharArray())
                    if (count.getOrDefault(c, 0) < countOf(t, c)) {
                        valid = false;
                        break;
                    }
                if (valid) {
                    String current = s.substring(left, right + 1);
                    if (answer.isEmpty() || current.length() < answer.length()) answer = current;
                    break;
                }
            }
        }
        return answer;
    }

    private int countOf(String t, char c) {
        int n = 0;
        for (char x : t.toCharArray()) if (x == c) n++;
        return n;
    }
}
