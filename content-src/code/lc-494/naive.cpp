class Solution {
public:
    int findTargetSumWays(vector<int>& nums, int target) {
        return dfs(nums, target, 0, 0);
    }

private:
    int dfs(vector<int>& nums, int target, int index, int total) {
        if (index == (int)nums.size()) return total == target ? 1 : 0;

        return dfs(nums, target, index + 1, total + nums[index])
             + dfs(nums, target, index + 1, total - nums[index]);
    }
};
