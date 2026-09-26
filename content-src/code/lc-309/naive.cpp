class Solution {
public:
    int maxProfit(vector<int>& prices) {
        return dfs(prices, 0, true);
    }

private:
    int dfs(vector<int>& prices, int i, bool buying) {
        if (i >= (int)prices.size()) return 0;

        if (buying) {
            int buy = -prices[i] + dfs(prices, i + 1, false);
            int skip = dfs(prices, i + 1, true);
            return max(buy, skip);
        }

        int sell = prices[i] + dfs(prices, i + 2, true);
        int hold = dfs(prices, i + 1, false);
        return max(sell, hold);
    }
};
