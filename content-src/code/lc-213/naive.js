var rob = function(nums) {
    const n = nums.length;

    const dfs = (i, firstRobbed, previousRobbed) => {
        if (i === n) return 0;

        const skip = dfs(i + 1, firstRobbed, false);

        let take = 0;
        if (!previousRobbed) {
            if (i !== n - 1 || !firstRobbed) {
                take = nums[i] + dfs(i + 1, firstRobbed || i === 0, true);
            }
        }

        return Math.max(skip, take);
    };

    return dfs(0, false, false);
};
