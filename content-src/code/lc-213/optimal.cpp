class Solution {
public:
    int rob(vector<int>& nums) {
        int n = nums.size();
        if (n == 1) return nums[0];

        return max(robLinear(nums, 0, n - 2), robLinear(nums, 1, n - 1));
    }

private:
    // Rob houses nums[lo..hi] laid out in a line
    int robLinear(vector<int>& nums, int lo, int hi) {
        int prev2 = 0, prev1 = 0;

        for (int i = lo; i <= hi; i++) {
            int current = max(prev1, nums[i] + prev2);
            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    }
};
