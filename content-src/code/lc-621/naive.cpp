class Solution {
public:
    int leastInterval(vector<char>& tasks, int n) {
        unordered_map<char, int> count;
        for (char task : tasks) count[task]++;

        int time = 0;

        while (!count.empty()) {
            int executed = 0;

            // Sort by frequency each round
            vector<char> available;
            for (auto& [task, freq] : count) available.push_back(task);
            sort(available.begin(), available.end(), [&](char a, char b) {
                return count[a] > count[b];
            });

            for (int i = 0; i < (int)available.size() && i < n + 1; i++) {
                char task = available[i];
                count[task]--;
                executed++;

                if (count[task] == 0) count.erase(task);
            }

            if (!count.empty()) time += n + 1;
            else time += executed;
        }

        return time;
    }
};
