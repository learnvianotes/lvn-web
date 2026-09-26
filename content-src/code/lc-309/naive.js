var maxProfit = function(prices) {
    const dfs = (i, buying) => {
        if (i >= prices.length) return 0;

        if (buying) {
            const buy = -prices[i] + dfs(i + 1, false);
            const skip = dfs(i + 1, true);
            return Math.max(buy, skip);
        }

        const sell = prices[i] + dfs(i + 2, true);
        const hold = dfs(i + 1, false);
        return Math.max(sell, hold);
    };

    return dfs(0, true);
};
