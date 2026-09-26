class Solution {
public:
    vector<string> findItinerary(vector<vector<string>>& tickets) {
        int n = tickets.size();
        sort(tickets.begin(), tickets.end());

        // airport -> indices of its tickets, in lexical order of destination
        unordered_map<string, vector<int>> graph;
        for (int i = 0; i < n; i++)
            graph[tickets[i][0]].push_back(i);

        vector<bool> used(n, false);
        vector<string> path{"JFK"};

        function<bool(const string&)> dfs = [&](const string& airport) -> bool {
            if ((int)path.size() == n + 1) return true;

            for (int i : graph[airport]) {
                if (used[i]) continue;

                used[i] = true;
                path.push_back(tickets[i][1]);

                if (dfs(tickets[i][1])) return true;

                used[i] = false;  // backtrack
                path.pop_back();
            }

            return false;
        };

        dfs("JFK");
        return path;
    }
};
