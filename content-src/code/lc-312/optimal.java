class Solution {
    public int maxCoins(int[] input) {
        int n = input.length + 2;
        int[] nums = new int[n];
        nums[0] = 1;
        nums[n - 1] = 1;
        for (int i = 0; i < input.length; i++) nums[i + 1] = input[i];

        int[][] dp = new int[n][n];

        for (int length = 2; length < n; length++) {
            for (int left = 0; left < n - length; left++) {
                int right = left + length;

                for (int k = left + 1; k < right; k++) {
                    int coins = nums[left] * nums[k] * nums[right];

                    dp[left][right] = Math.max(dp[left][right],
                                               dp[left][k] + coins + dp[k][right]);
                }
            }
        }

        return dp[0][n - 1];
    }
}
