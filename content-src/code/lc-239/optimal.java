class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        int[] result = new int[nums.length - k + 1];
        Deque<Integer> dq = new ArrayDeque<>();
        for (int right = 0; right < nums.length; right++) {
            // Remove smaller values
            while (!dq.isEmpty() && nums[dq.peekLast()] <= nums[right]) dq.pollLast();
            dq.offerLast(right);
            // Remove indices outside window
            int left = right - k + 1;
            if (dq.peekFirst() < left) dq.pollFirst();
            if (right >= k - 1) result[left] = nums[dq.peekFirst()];
        }
        return result;
    }
}
