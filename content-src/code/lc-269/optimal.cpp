class Solution {
public:
    string alienOrder(vector<string>& words) {
        unordered_map<char, unordered_set<char>> graph;
        for (auto& word : words)
            for (char c : word) graph[c];

        for (int i = 0; i + 1 < (int)words.size(); i++) {
            const string& w1 = words[i];
            const string& w2 = words[i + 1];
            int minLength = min(w1.size(), w2.size());

            if (w1.size() > w2.size() && w1.compare(0, minLength, w2, 0, minLength) == 0)
                return "";

            for (int j = 0; j < minLength; j++) {
                if (w1[j] != w2[j]) {
                    graph[w1[j]].insert(w2[j]);
                    break;
                }
            }
        }

        // true = on the current path (cycle), false = finished
        unordered_map<char, bool> visited;
        string result;

        function<bool(char)> dfs = [&](char c) -> bool {
            if (visited.count(c)) return visited[c];

            visited[c] = true;

            for (char neighbor : graph[c])
                if (dfs(neighbor)) return true;

            visited[c] = false;
            result += c;

            return false;
        };

        for (auto& [c, _] : graph)
            if (dfs(c)) return "";

        reverse(result.begin(), result.end());
        return result;
    }
};
