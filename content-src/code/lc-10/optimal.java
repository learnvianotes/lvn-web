class Solution {
    // memo[i][j]: null = not computed yet
    private Boolean[][] memo;

    public boolean isMatch(String s, String p) {
        memo = new Boolean[s.length() + 1][p.length() + 1];
        return dfs(s, p, 0, 0);
    }

    private boolean dfs(String s, String p, int i, int j) {
        if (memo[i][j] != null) return memo[i][j];

        if (j == p.length()) return i == s.length();

        boolean firstMatch = i < s.length()
            && (p.charAt(j) == s.charAt(i) || p.charAt(j) == '.');
        boolean answer;

        if (j + 1 < p.length() && p.charAt(j + 1) == '*') {
            answer = dfs(s, p, i, j + 2) || (firstMatch && dfs(s, p, i + 1, j));
        } else {
            answer = firstMatch && dfs(s, p, i + 1, j + 1);
        }

        memo[i][j] = answer;
        return answer;
    }
}
