var findTargetSumWays = function(nums, target) {
    const dfs = (index, total) => {
        if (index === nums.length) return total === target ? 1 : 0;

        return dfs(index + 1, total + nums[index])
             + dfs(index + 1, total - nums[index]);
    };

    return dfs(0, 0);
};
