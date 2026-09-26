var coinChange = function(coins, amount) {
    const dp = new Array(amount + 1).fill(amount + 1);
    dp[0] = 0;

    for (let current = 1; current <= amount; current++) {
        for (const coin of coins) {
            if (coin <= current) {
                dp[current] = Math.min(dp[current], dp[current - coin] + 1);
            }
        }
    }

    return dp[amount] > amount ? -1 : dp[amount];
};
