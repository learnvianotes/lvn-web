var maxCoins = function(nums) {
    const dfs = (nums) => {
        if (nums.length === 0) return 0;

        let answer = 0;

        for (let i = 0; i < nums.length; i++) {
            const left = i > 0 ? nums[i - 1] : 1;
            const right = i + 1 < nums.length ? nums[i + 1] : 1;

            const coins = left * nums[i] * right;

            const remaining = [...nums.slice(0, i), ...nums.slice(i + 1)];

            answer = Math.max(answer, coins + dfs(remaining));
        }

        return answer;
    };

    return dfs(nums);
};
