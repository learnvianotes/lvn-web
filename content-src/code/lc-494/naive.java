class Solution {
    public int findTargetSumWays(int[] nums, int target) {
        return dfs(nums, target, 0, 0);
    }

    private int dfs(int[] nums, int target, int index, int total) {
        if (index == nums.length) return total == target ? 1 : 0;

        return dfs(nums, target, index + 1, total + nums[index])
             + dfs(nums, target, index + 1, total - nums[index]);
    }
}
