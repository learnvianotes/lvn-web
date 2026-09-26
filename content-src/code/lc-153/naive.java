class Solution {
    public int findMin(int[] nums) {
        int answer = nums[0];

        for (int num : nums) {
            answer = Math.min(answer, num);
        }

        return answer;
    }
}
