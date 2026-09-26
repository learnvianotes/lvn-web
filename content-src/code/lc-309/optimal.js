var maxProfit = function(prices) {
    const memo = new Map();

    const dfs = (i, buying) => {
        if (i >= prices.length) return 0;

        const key = `${i},${buying}`;
        if (memo.has(key)) return memo.get(key);

        let result;

        if (buying) {
            const buy = -prices[i] + dfs(i + 1, false);
            const skip = dfs(i + 1, true);
            result = Math.max(buy, skip);
        } else {
            const sell = prices[i] + dfs(i + 2, true);
            const hold = dfs(i + 1, false);
            result = Math.max(sell, hold);
        }

        memo.set(key, result);
        return result;
    };

    return dfs(0, true);
};
