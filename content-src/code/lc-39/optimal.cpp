class Solution {
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> result;
        vector<int> current;
        sort(candidates.begin(), candidates.end());
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
            int num = candidates[i];

            if (num > remaining) break;

            current.push_back(num);

            // i, not i + 1, because we can reuse the same number
            backtrack(candidates, i, remaining - num, current, result);

            current.pop_back();
        }
    }
};
