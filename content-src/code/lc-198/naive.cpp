class Solution {
public:
    int rob(vector<int>& nums) {
        return dfs(nums, 0);
    }

private:
    int dfs(vector<int>& nums, int i) {
        if (i >= (int)nums.size()) return 0;

        int robIt = nums[i] + dfs(nums, i + 2);
        int skip = dfs(nums, i + 1);

        return max(robIt, skip);
    }
};
