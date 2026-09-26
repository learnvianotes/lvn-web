var maxCoins = function(nums) {
    nums = [1, ...nums, 1];
    const n = nums.length;

    const dp = Array.from({ length: n }, () => new Array(n).fill(0));

    for (let length = 2; length < n; length++) {
        for (let left = 0; left < n - length; left++) {
            const right = left + length;

            for (let k = left + 1; k < right; k++) {
                const coins = nums[left] * nums[k] * nums[right];

                dp[left][right] = Math.max(
                    dp[left][right],
                    dp[left][k] + coins + dp[k][right]
                );
            }
        }
    }

    return dp[0][n - 1];
};
