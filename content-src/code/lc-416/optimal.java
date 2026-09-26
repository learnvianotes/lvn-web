class Solution {
    public boolean canPartition(int[] nums) {
        int total = 0;
        for (int num : nums) total += num;

        if (total % 2 != 0) return false;

        int target = total / 2;

        boolean[] dp = new boolean[target + 1];
        dp[0] = true;

        for (int num : nums) {
            for (int current = target; current >= num; current--) {
                dp[current] = dp[current] || dp[current - num];
            }
        }

        return dp[target];
    }
}
