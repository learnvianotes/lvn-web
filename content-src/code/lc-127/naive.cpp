class Solution {
public:
    int ladderLength(string beginWord, string endWord, vector<string>& wordList) {
        if (find(wordList.begin(), wordList.end(), endWord) == wordList.end())
            return 0;

        vector<string> words = wordList;
        words.push_back(beginWord);
        int n = words.size();

        auto oneApart = [](const string& a, const string& b) {
            int diff = 0;
            for (int i = 0; i < (int)a.size() && diff <= 1; i++)
                if (a[i] != b[i]) diff++;
            return diff == 1;
        };

        // Compare every pair of words to build the graph
        vector<vector<int>> graph(n);
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (oneApart(words[i], words[j])) {
                    graph[i].push_back(j);
                    graph[j].push_back(i);
                }
            }
        }

        vector<bool> visited(n, false);
        queue<pair<int, int>> q;
        q.push({n - 1, 1});
        visited[n - 1] = true;

        while (!q.empty()) {
            auto [i, distance] = q.front();
            q.pop();

            if (words[i] == endWord) return distance;

            for (int j : graph[i]) {
                if (!visited[j]) {
                    visited[j] = true;
                    q.push({j, distance + 1});
                }
            }
        }

        return 0;
    }
};
