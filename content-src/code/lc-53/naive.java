class Solution {
    public int maxSubArray(int[] nums) {
        int answer = Integer.MIN_VALUE;

        for (int i = 0; i < nums.length; i++) {
            int total = 0;

            for (int j = i; j < nums.length; j++) {
                total += nums[j];
                answer = Math.max(answer, total);
            }
        }

        return answer;
    }
}
