class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        int[] result = new int[nums.length - k + 1];
        for (int i = 0; i + k <= nums.length; i++) {
            int best = nums[i];
            for (int j = i + 1; j < i + k; j++) best = Math.max(best, nums[j]);
            result[i] = best;
        }
        return result;
    }
}
