class Solution {
    public boolean checkValidString(String s) {
        return dfs(s, 0, 0);
    }

    private boolean dfs(String s, int index, int balance) {
        if (balance < 0) {
            return false;
        }

        if (index == s.length()) {
            return balance == 0;
        }

        char c = s.charAt(index);

        if (c == '(') {
            return dfs(s, index + 1, balance + 1);
        }

        if (c == ')') {
            return dfs(s, index + 1, balance - 1);
        }

        // Try '*' as '(', ')', or ''
        return dfs(s, index + 1, balance + 1)
            || dfs(s, index + 1, balance - 1)
            || dfs(s, index + 1, balance);
    }
}
