class Solution {
    public List<List<String>> partition(String s) {
        int n = s.length();

        boolean[][] palindrome = new boolean[n][n];

        for (int i = 0; i < n; i++) palindrome[i][i] = true;

        for (int length = 2; length <= n; length++) {
            for (int left = 0; left <= n - length; left++) {
                int right = left + length - 1;

                if (s.charAt(left) == s.charAt(right)) {
                    if (length == 2 || palindrome[left + 1][right - 1]) {
                        palindrome[left][right] = true;
                    }
                }
            }
        }

        List<List<String>> result = new ArrayList<>();
        backtrack(s, 0, palindrome, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(String s, int start, boolean[][] palindrome,
                           List<String> current, List<List<String>> result) {
        int n = s.length();

        if (start == n) {
            result.add(new ArrayList<>(current));
            return;
        }

        for (int end = start; end < n; end++) {
            if (palindrome[start][end]) {
                current.add(s.substring(start, end + 1));
                backtrack(s, end + 1, palindrome, current, result);
                current.remove(current.size() - 1);
            }
        }
    }
}
