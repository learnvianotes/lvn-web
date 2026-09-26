class Solution {
public:
    int lengthOfLIS(vector<int>& nums) {
        return dfs(nums, 0, -1);
    }

private:
    int dfs(vector<int>& nums, int index, int previous) {
        if (index == (int)nums.size()) return 0;

        int skip = dfs(nums, index + 1, previous);

        int take = 0;
        if (previous == -1 || nums[index] > nums[previous]) {
            take = 1 + dfs(nums, index + 1, index);
        }

        return max(take, skip);
    }
};
