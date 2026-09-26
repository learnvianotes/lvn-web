class Solution {
    public boolean isInterleave(String s1, String s2, String s3) {
        if (s1.length() + s2.length() != s3.length()) return false;
        return dfs(s1, s2, s3, 0, 0);
    }

    private boolean dfs(String s1, String s2, String s3, int i, int j) {
        int k = i + j;
        if (k == s3.length()) return true;

        if (i < s1.length() && s1.charAt(i) == s3.charAt(k)) {
            if (dfs(s1, s2, s3, i + 1, j)) return true;
        }

        if (j < s2.length() && s2.charAt(j) == s3.charAt(k)) {
            if (dfs(s1, s2, s3, i, j + 1)) return true;
        }

        return false;
    }
}
