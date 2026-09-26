var canPartition = function(nums) {
    const total = nums.reduce((a, b) => a + b, 0);
    if (total % 2) return false;

    const target = total / 2;

    const dfs = (index, remaining) => {
        if (remaining === 0) return true;
        if (index === nums.length || remaining < 0) return false;

        return dfs(index + 1, remaining - nums[index])
            || dfs(index + 1, remaining);
    };

    return dfs(0, target);
};
