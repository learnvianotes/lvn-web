var lengthOfLIS = function(nums) {
    const dfs = (index, previous) => {
        if (index === nums.length) return 0;

        const skip = dfs(index + 1, previous);

        let take = 0;
        if (previous === -1 || nums[index] > nums[previous]) {
            take = 1 + dfs(index + 1, index);
        }

        return Math.max(take, skip);
    };

    return dfs(0, -1);
};
