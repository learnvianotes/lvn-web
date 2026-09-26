class Solution {
public:
    int maxProfit(vector<int>& prices) {
        // memo[i][buying], -1 = not computed yet
        memo.assign(prices.size(), vector<int>(2, -1));
        return dfs(prices, 0, true);
    }

private:
    vector<vector<int>> memo;

    int dfs(vector<int>& prices, int i, bool buying) {
        if (i >= (int)prices.size()) return 0;

        int& cached = memo[i][buying];
        if (cached != -1) return cached;

        if (buying) {
            int buy = -prices[i] + dfs(prices, i + 1, false);
            int skip = dfs(prices, i + 1, true);
            cached = max(buy, skip);
        } else {
            int sell = prices[i] + dfs(prices, i + 2, true);
            int hold = dfs(prices, i + 1, false);
            cached = max(sell, hold);
        }

        return cached;
    }
};
