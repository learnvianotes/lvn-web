class Solution {
    // memo[i][buying ? 1 : 0], null = not computed yet
    private Integer[][] memo;

    public int maxProfit(int[] prices) {
        memo = new Integer[prices.length][2];
        return dfs(prices, 0, true);
    }

    private int dfs(int[] prices, int i, boolean buying) {
        if (i >= prices.length) return 0;

        int b = buying ? 1 : 0;
        if (memo[i][b] != null) return memo[i][b];

        if (buying) {
            int buy = -prices[i] + dfs(prices, i + 1, false);
            int skip = dfs(prices, i + 1, true);
            memo[i][b] = Math.max(buy, skip);
        } else {
            int sell = prices[i] + dfs(prices, i + 2, true);
            int hold = dfs(prices, i + 1, false);
            memo[i][b] = Math.max(sell, hold);
        }

        return memo[i][b];
    }
}
