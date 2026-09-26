var coinChange = function(coins, amount) {
    const dfs = (remaining) => {
        if (remaining === 0) return 0;
        if (remaining < 0) return Infinity;

        let answer = Infinity;

        for (const coin of coins) {
            answer = Math.min(answer, 1 + dfs(remaining - coin));
        }

        return answer;
    };

    const result = dfs(amount);

    return result === Infinity ? -1 : result;
};
