class Solution {
    public int findKthLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();  // min-heap

        for (int num : nums) {
            heap.offer(num);

            if (heap.size() > k) heap.poll();
        }

        return heap.peek();
    }
}

// --- Alternative: Quickselect O(n) average ---
class SolutionQuickselect {
    public int findKthLargest(int[] nums, int k) {
        return quickselect(nums, 0, nums.length - 1, nums.length - k);
    }

    private int quickselect(int[] nums, int left, int right, int target) {
        int pivot = nums[right];
        int partitionIndex = left;

        for (int i = left; i < right; i++) {
            if (nums[i] <= pivot) {
                swap(nums, i, partitionIndex);
                partitionIndex++;
            }
        }

        swap(nums, partitionIndex, right);

        if (partitionIndex == target) return nums[partitionIndex];

        if (partitionIndex < target) return quickselect(nums, partitionIndex + 1, right, target);

        return quickselect(nums, left, partitionIndex - 1, target);
    }

    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
}
