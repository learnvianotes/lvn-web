class Solution {
    public int climbStairs(int n) {
        return dfs(0, n);
    }

    private int dfs(int step, int n) {
        if (step == n) return 1;
        if (step > n) return 0;
        return dfs(step + 1, n) + dfs(step + 2, n);
    }
}
