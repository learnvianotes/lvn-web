class Solution {
    public boolean canPartition(int[] nums) {
        int total = 0;
        for (int num : nums) total += num;

        if (total % 2 != 0) return false;

        return dfs(nums, 0, total / 2);
    }

    private boolean dfs(int[] nums, int index, int remaining) {
        if (remaining == 0) return true;
        if (index == nums.length || remaining < 0) return false;

        return dfs(nums, index + 1, remaining - nums[index])
            || dfs(nums, index + 1, remaining);
    }
}
