class Solution {
public:
    int findKthLargest(vector<int>& nums, int k) {
        priority_queue<int, vector<int>, greater<int>> heap;  // min-heap

        for (int num : nums) {
            heap.push(num);

            if ((int)heap.size() > k) heap.pop();
        }

        return heap.top();
    }
};

// --- Alternative: Quickselect O(n) average ---
class SolutionQuickselect {
public:
    int findKthLargest(vector<int>& nums, int k) {
        int target = nums.size() - k;

        function<int(int, int)> quickselect = [&](int left, int right) {
            int pivot = nums[right];
            int partitionIndex = left;

            for (int i = left; i < right; i++) {
                if (nums[i] <= pivot) {
                    swap(nums[i], nums[partitionIndex]);
                    partitionIndex++;
                }
            }

            swap(nums[partitionIndex], nums[right]);

            if (partitionIndex == target) return nums[partitionIndex];

            if (partitionIndex < target) return quickselect(partitionIndex + 1, right);

            return quickselect(left, partitionIndex - 1);
        };

        return quickselect(0, nums.size() - 1);
    }
};
