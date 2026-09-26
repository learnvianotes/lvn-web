class Solution {
public:
    int eraseOverlapIntervals(vector<vector<int>>& intervals) {
        int n = intervals.size();
        int best = n;
        vector<vector<int>> chosen;
        dfs(intervals, 0, chosen, best);
        return best;
    }

private:
    bool overlaps(const vector<int>& a, const vector<int>& b) {
        return a[0] < b[1] && b[0] < a[1];
    }

    void dfs(vector<vector<int>>& intervals, int index, vector<vector<int>>& chosen, int& best) {
        int n = intervals.size();

        if (index == n) {
            best = min(best, n - (int)chosen.size());
            return;
        }

        // Skip this interval
        dfs(intervals, index + 1, chosen, best);

        // Take if compatible
        bool compatible = true;
        for (auto& x : chosen) {
            if (overlaps(intervals[index], x)) {
                compatible = false;
                break;
            }
        }

        if (compatible) {
            chosen.push_back(intervals[index]);
            dfs(intervals, index + 1, chosen, best);
            chosen.pop_back();
        }
    }
};
