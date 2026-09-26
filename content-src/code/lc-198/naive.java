class Solution {
    public int rob(int[] nums) {
        return dfs(nums, 0);
    }

    private int dfs(int[] nums, int i) {
        if (i >= nums.length) return 0;

        int rob = nums[i] + dfs(nums, i + 2);
        int skip = dfs(nums, i + 1);

        return Math.max(rob, skip);
    }
}
