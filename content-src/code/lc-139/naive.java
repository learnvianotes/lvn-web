class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        Set<String> words = new HashSet<>(wordDict);
        return dfs(s, words, 0);
    }

    private boolean dfs(String s, Set<String> words, int start) {
        if (start == s.length()) return true;

        for (int end = start + 1; end <= s.length(); end++) {
            if (words.contains(s.substring(start, end))) {
                if (dfs(s, words, end)) return true;
            }
        }

        return false;
    }
}
