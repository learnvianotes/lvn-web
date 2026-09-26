class Solution {
    public boolean isMatch(String s, String p) {
        return dfs(s, p, 0, 0);
    }

    private boolean dfs(String s, String p, int i, int j) {
        if (j == p.length()) return i == s.length();

        boolean firstMatch = i < s.length()
            && (p.charAt(j) == s.charAt(i) || p.charAt(j) == '.');

        if (j + 1 < p.length() && p.charAt(j + 1) == '*') {
            return dfs(s, p, i, j + 2) || (firstMatch && dfs(s, p, i + 1, j));
        }

        return firstMatch && dfs(s, p, i + 1, j + 1);
    }
}
