class Solution {
    private int answer;

    public int jump(int[] nums) {
        answer = Integer.MAX_VALUE;
        dfs(nums, 0, 0);
        return answer;
    }

    private void dfs(int[] nums, int index, int jumps) {
        int n = nums.length;

        if (index >= n - 1) {
            answer = Math.min(answer, jumps);
            return;
        }

        if (jumps >= answer) {
            return;
        }

        for (int jump = 1; jump <= nums[index]; jump++) {
            dfs(nums, index + jump, jumps + 1);
        }
    }
}
