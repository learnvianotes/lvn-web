class Solution {
    public int findKthLargest(int[] nums, int k) {
        Arrays.sort(nums);

        // Sorted ascending, so the kth largest is k from the end
        return nums[nums.length - k];
    }
}
