var findTargetSumWays = function(nums, target) {
    const memo = new Map();

    const dfs = (index, total) => {
        if (index === nums.length) return total === target ? 1 : 0;

        const key = `${index},${total}`;
        if (memo.has(key)) return memo.get(key);

        const ways = dfs(index + 1, total + nums[index])
                   + dfs(index + 1, total - nums[index]);

        memo.set(key, ways);
        return ways;
    };

    return dfs(0, 0);
};
