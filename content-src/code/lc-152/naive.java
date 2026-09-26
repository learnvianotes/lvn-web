class Solution {
    public int maxProduct(int[] nums) {
        long answer = nums[0];

        for (int i = 0; i < nums.length; i++) {
            long product = 1;

            for (int j = i; j < nums.length; j++) {
                product *= nums[j];
                answer = Math.max(answer, product);
            }
        }

        return (int) answer;
    }
}
