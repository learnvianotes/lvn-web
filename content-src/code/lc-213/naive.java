class Solution {
    public int rob(int[] nums) {
        return dfs(nums, 0, false, false);
    }

    private int dfs(int[] nums, int i, boolean firstRobbed, boolean previousRobbed) {
        int n = nums.length;
        if (i == n) return 0;

        int skip = dfs(nums, i + 1, firstRobbed, false);

        int take = 0;
        if (!previousRobbed) {
            if (i != n - 1 || !firstRobbed) {
                take = nums[i] + dfs(nums, i + 1, firstRobbed || i == 0, true);
            }
        }

        return Math.max(skip, take);
    }
}
