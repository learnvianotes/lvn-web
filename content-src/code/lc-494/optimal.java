class Solution {
    private Map<String, Integer> memo;

    public int findTargetSumWays(int[] nums, int target) {
        memo = new HashMap<>();
        return dfs(nums, target, 0, 0);
    }

    private int dfs(int[] nums, int target, int index, int total) {
        if (index == nums.length) return total == target ? 1 : 0;

        String key = index + "," + total;
        if (memo.containsKey(key)) return memo.get(key);

        int ways = dfs(nums, target, index + 1, total + nums[index])
                 + dfs(nums, target, index + 1, total - nums[index]);

        memo.put(key, ways);
        return ways;
    }
}
