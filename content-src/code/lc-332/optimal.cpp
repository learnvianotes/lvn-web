class Solution {
public:
    vector<string> findItinerary(vector<vector<string>>& tickets) {
        unordered_map<string, vector<string>> graph;

        sort(tickets.rbegin(), tickets.rend());

        for (auto& t : tickets)
            graph[t[0]].push_back(t[1]);

        vector<string> itinerary;

        function<void(const string&)> dfs = [&](const string& airport) {
            auto& destinations = graph[airport];

            while (!destinations.empty()) {
                string next = destinations.back();
                destinations.pop_back();
                dfs(next);
            }

            itinerary.push_back(airport);
        };

        dfs("JFK");
        reverse(itinerary.begin(), itinerary.end());
        return itinerary;
    }
};
