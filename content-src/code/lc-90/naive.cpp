class Solution {
public:
    vector<vector<int>> subsetsWithDup(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        set<vector<int>> result;
        vector<int> current;
        backtrack(nums, 0, current, result);
        return vector<vector<int>>(result.begin(), result.end());
    }

private:
    void backtrack(vector<int>& nums, int index, vector<int>& current, set<vector<int>>& result) {
        if (index == (int)nums.size()) {
            result.insert(current);
            return;
        }

        // Don't take
        backtrack(nums, index + 1, current, result);

        // Take
        current.push_back(nums[index]);
        backtrack(nums, index + 1, current, result);
        current.pop_back();
    }
};
