class Solution {
public:
    int ladderLength(string beginWord, string endWord, vector<string>& wordList) {
        if (find(wordList.begin(), wordList.end(), endWord) == wordList.end())
            return 0;

        unordered_map<string, vector<string>> patterns;

        for (const string& word : wordList) {
            for (int i = 0; i < (int)word.size(); i++) {
                string pattern = word.substr(0, i) + "*" + word.substr(i + 1);
                patterns[pattern].push_back(word);
            }
        }

        unordered_set<string> visited{beginWord};
        queue<pair<string, int>> q;
        q.push({beginWord, 1});

        while (!q.empty()) {
            auto [word, distance] = q.front();
            q.pop();

            if (word == endWord) return distance;

            for (int i = 0; i < (int)word.size(); i++) {
                string pattern = word.substr(0, i) + "*" + word.substr(i + 1);

                for (const string& neighbor : patterns[pattern]) {
                    if (!visited.count(neighbor)) {
                        visited.insert(neighbor);
                        q.push({neighbor, distance + 1});
                    }
                }

                patterns[pattern].clear();
            }
        }

        return 0;
    }
};
