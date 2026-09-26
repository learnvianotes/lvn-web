class Solution {
public:
    int leastInterval(vector<char>& tasks, int n) {
        unordered_map<char, int> count;
        for (char task : tasks) count[task]++;

        priority_queue<int> heap;  // max-heap of remaining counts
        for (auto& [task, freq] : count) heap.push(freq);

        queue<pair<int, int>> cooldown;  // {remaining, time it becomes available}

        int time = 0;

        while (!heap.empty() || !cooldown.empty()) {
            time++;

            // Add tasks whose cooldown is over
            while (!cooldown.empty() && cooldown.front().second == time) {
                heap.push(cooldown.front().first);
                cooldown.pop();
            }

            if (!heap.empty()) {
                int freq = heap.top() - 1;
                heap.pop();

                if (freq != 0) cooldown.push({freq, time + n + 1});
            }
        }

        return time;
    }
};
