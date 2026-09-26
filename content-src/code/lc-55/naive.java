class Solution {
    public boolean canJump(int[] nums) {
        return dfs(nums, 0);
    }

    private boolean dfs(int[] nums, int index) {
        int n = nums.length;
        if (index >= n - 1) {
            return true;
        }

        int maxJump = nums[index];

        for (int jump = 1; jump <= maxJump; jump++) {
            if (dfs(nums, index + jump)) {
                return true;
            }
        }

        return false;
    }
}
