class Solution {
public:
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        set<vector<int>> result;
        vector<int> current;
        sort(candidates.begin(), candidates.end());
        backtrack(candidates, 0, target, current, result);
        return vector<vector<int>>(result.begin(), result.end());
    }

private:
    void backtrack(vector<int>& candidates, int index, int remaining, vector<int>& current,
                   set<vector<int>>& result) {
        if (remaining == 0) {
            result.insert(current);
            return;
        }

        if (index == (int)candidates.size() || remaining < 0) return;

        // Don't choose
        backtrack(candidates, index + 1, remaining, current, result);

        // Choose
        current.push_back(candidates[index]);
        backtrack(candidates, index + 1, remaining - candidates[index], current, result);
        current.pop_back();
    }
};
