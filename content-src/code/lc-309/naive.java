class Solution {
    public int maxProfit(int[] prices) {
        return dfs(prices, 0, true);
    }

    private int dfs(int[] prices, int i, boolean buying) {
        if (i >= prices.length) return 0;

        if (buying) {
            int buy = -prices[i] + dfs(prices, i + 1, false);
            int skip = dfs(prices, i + 1, true);
            return Math.max(buy, skip);
        }

        int sell = prices[i] + dfs(prices, i + 2, true);
        int hold = dfs(prices, i + 1, false);
        return Math.max(sell, hold);
    }
}
