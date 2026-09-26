class Solution {
public:
    vector<int> minInterval(vector<vector<int>>& intervals, vector<int>& queries) {
        sort(intervals.begin(), intervals.end());

        vector<pair<int, int>> sortedQueries;  // {query, original index}
        for (int i = 0; i < (int)queries.size(); i++) sortedQueries.push_back({queries[i], i});
        sort(sortedQueries.begin(), sortedQueries.end());

        vector<int> result(queries.size(), -1);
        // min-heap of {size, end}
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> heap;
        int i = 0;

        for (auto [query, originalIndex] : sortedQueries) {
            // Add all intervals whose start <= query
            while (i < (int)intervals.size() && intervals[i][0] <= query) {
                int start = intervals[i][0], end = intervals[i][1];
                int size = end - start + 1;
                heap.push({size, end});
                i++;
            }

            // Remove intervals that ended before this query
            while (!heap.empty() && heap.top().second < query) heap.pop();

            if (!heap.empty()) result[originalIndex] = heap.top().first;
        }

        return result;
    }
};
