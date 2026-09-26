class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int total = accumulate(nums.begin(), nums.end(), 0);
        if (total % 2) return false;

        return dfs(nums, 0, total / 2);
    }

private:
    bool dfs(vector<int>& nums, int index, int remaining) {
        if (remaining == 0) return true;
        if (index == (int)nums.size() || remaining < 0) return false;

        return dfs(nums, index + 1, remaining - nums[index])
            || dfs(nums, index + 1, remaining);
    }
};
