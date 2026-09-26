class Solution {
public:
    vector<int> minInterval(vector<vector<int>>& intervals, vector<int>& queries) {
        vector<int> result;

        for (int query : queries) {
            int best = INT_MAX;

            for (auto& interval : intervals) {
                int start = interval[0], end = interval[1];

                if (start <= query && query <= end) {
                    int size = end - start + 1;
                    best = min(best, size);
                }
            }

            result.push_back(best == INT_MAX ? -1 : best);
        }

        return result;
    }
};
