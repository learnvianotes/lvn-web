class Solution {
    public int change(int amount, int[] coins) {
        return dfs(coins, 0, amount);
    }

    private int dfs(int[] coins, int index, int remaining) {
        if (remaining == 0) return 1;
        if (index == coins.length || remaining < 0) return 0;

        // Use current coin
        int use = dfs(coins, index, remaining - coins[index]);

        // Skip current coin
        int skip = dfs(coins, index + 1, remaining);

        return use + skip;
    }
}
