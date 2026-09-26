class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& input) {
        vector<vector<int>> intervals = input;
        bool changed = true;

        while (changed) {
            changed = false;
            vector<vector<int>> result;
            vector<bool> used(intervals.size(), false);

            for (int i = 0; i < (int)intervals.size(); i++) {
                if (used[i]) continue;

                vector<int> current = intervals[i];

                for (int j = i + 1; j < (int)intervals.size(); j++) {
                    if (used[j]) continue;

                    vector<int>& other = intervals[j];

                    if (current[0] <= other[1] && other[0] <= current[1]) {
                        current = {
                            min(current[0], other[0]),
                            max(current[1], other[1]),
                        };
                        used[j] = true;
                        changed = true;
                    }
                }

                result.push_back(current);
            }

            intervals = result;
        }

        return intervals;
    }
};
