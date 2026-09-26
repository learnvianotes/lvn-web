class Solution {
    public boolean checkInclusion(String s1, String s2) {
        Set<String> target = new HashSet<>();
        permute(s1.toCharArray(), 0, target);
        int length = s1.length();
        for (int i = 0; i + length <= s2.length(); i++)
            if (target.contains(s2.substring(i, i + length))) return true;
        return false;
    }

    private void permute(char[] chars, int start, Set<String> target) {
        if (start == chars.length) { target.add(new String(chars)); return; }
        for (int i = start; i < chars.length; i++) {
            char t = chars[start]; chars[start] = chars[i]; chars[i] = t;
            permute(chars, start + 1, target);
            t = chars[start]; chars[start] = chars[i]; chars[i] = t;
        }
    }
}
