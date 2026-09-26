class Solution {
    public int maxProduct(int[] nums) {
        long currentMax = nums[0];
        long currentMin = nums[0];
        long answer = nums[0];

        for (int i = 1; i < nums.length; i++) {
            long num = nums[i];

            if (num < 0) {
                long temp = currentMax;
                currentMax = currentMin;
                currentMin = temp;
            }

            currentMax = Math.max(num, currentMax * num);
            currentMin = Math.min(num, currentMin * num);

            answer = Math.max(answer, currentMax);
        }

        return (int) answer;
    }
}
