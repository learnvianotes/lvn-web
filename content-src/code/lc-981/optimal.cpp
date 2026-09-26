class TimeMap {
    unordered_map<string, vector<pair<int, string>>> store;

public:
    TimeMap() {}

    void set(string key, string value, int timestamp) {
        store[key].push_back({timestamp, value});
    }

    string get(string key, int timestamp) {
        auto it = store.find(key);
        if (it == store.end()) {
            return "";
        }

        const auto& values = it->second;

        int left = 0;
        int right = values.size() - 1;

        string answer = "";

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (values[mid].first <= timestamp) {
                answer = values[mid].second;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return answer;
    }
};
