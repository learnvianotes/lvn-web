class Solution {
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> result;
        vector<int> current;
        backtrack(candidates, target, 0, current, 0, result);
        return result;
    }

private:
    void backtrack(vector<int>& candidates, int target, int start, vector<int>& current, int total,
                   vector<vector<int>>& result) {
        if (total == target) {
            result.push_back(current);
            return;
        }

        if (total > target) return;

        for (int i = start; i < (int)candidates.size(); i++) {
            current.push_back(candidates[i]);
            backtrack(candidates, target, i, current, total + candidates[i], result);
            current.pop_back();
        }
    }
};
