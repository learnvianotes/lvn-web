class Solution {
public:
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        sort(candidates.begin(), candidates.end());
        vector<vector<int>> result;
        vector<int> current;
        backtrack(candidates, 0, target, current, result);
        return result;
    }

private:
    void backtrack(vector<int>& candidates, int start, int remaining, vector<int>& current,
                   vector<vector<int>>& result) {
        if (remaining == 0) {
            result.push_back(current);
            return;
        }

        for (int i = start; i < (int)candidates.size(); i++) {
            // Skip duplicate choices at the same level
            if (i > start && candidates[i] == candidates[i - 1]) continue;

            // Since sorted, no later value can work
            if (candidates[i] > remaining) break;

            current.push_back(candidates[i]);

            // i + 1 because each element can be used once
            backtrack(candidates, i + 1, remaining - candidates[i], current, result);

            current.pop_back();
        }
    }
};
