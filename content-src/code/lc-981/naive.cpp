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

        for (int i = values.size() - 1; i >= 0; i--) {
            if (values[i].first <= timestamp) {
                return values[i].second;
            }
        }

        return "";
    }
};
