class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        vector<vector<int>> result;
        vector<int> current;
        backtrack(nums, 0, current, result);
        return result;
    }

private:
    void backtrack(vector<int>& nums, int index, vector<int>& current, vector<vector<int>>& result) {
        if (index == (int)nums.size()) {
            result.push_back(current);
            return;
        }

        // Don't take nums[index]
        backtrack(nums, index + 1, current, result);

        // Take nums[index]
        current.push_back(nums[index]);
        backtrack(nums, index + 1, current, result);
        current.pop_back();
    }
};
