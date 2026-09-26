var rob = function(nums) {
    const dfs = (i) => {
        if (i >= nums.length) return 0;

        const robIt = nums[i] + dfs(i + 2);
        const skip = dfs(i + 1);

        return Math.max(robIt, skip);
    };

    return dfs(0);
};
