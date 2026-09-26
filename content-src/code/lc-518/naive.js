var change = function(amount, coins) {
    const dfs = (index, remaining) => {
        if (remaining === 0) return 1;
        if (index === coins.length || remaining < 0) return 0;

        // Use current coin
        const use = dfs(index, remaining - coins[index]);

        // Skip current coin
        const skip = dfs(index + 1, remaining);

        return use + skip;
    };

    return dfs(0, amount);
};
