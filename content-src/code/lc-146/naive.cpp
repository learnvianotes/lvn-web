class LRUCache {
    int capacity;
    unordered_map<int, int> cache;
    deque<int> order;

public:
    LRUCache(int capacity) : capacity(capacity) {}

    int get(int key) {
        if (!cache.count(key)) {
            return -1;
        }

        order.erase(find(order.begin(), order.end(), key));
        order.push_back(key);

        return cache[key];
    }

    void put(int key, int value) {
        if (cache.count(key)) {
            order.erase(find(order.begin(), order.end(), key));
        }

        cache[key] = value;
        order.push_back(key);

        if (cache.size() > capacity) {
            int oldest = order.front();
            order.pop_front();
            cache.erase(oldest);
        }
    }
};
