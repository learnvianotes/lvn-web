var canJump = function(nums) {
    const n = nums.length;

    const dfs = (index) => {
        if (index >= n - 1) {
            return true;
        }

        const maxJump = nums[index];

        for (let jump = 1; jump <= maxJump; jump++) {
            if (dfs(index + jump)) {
                return true;
            }
        }

        return false;
    };

    return dfs(0);
};
