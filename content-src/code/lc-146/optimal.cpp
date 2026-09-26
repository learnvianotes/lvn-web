class LRUCache {
    struct Node {
        int key, value;
        Node* prev = nullptr;
        Node* next = nullptr;
        Node(int key = 0, int value = 0) : key(key), value(value) {}
    };

    int capacity;
    unordered_map<int, Node*> cache;
    Node* left;
    Node* right;

    void remove(Node* node) {
        Node* previous = node->prev;
        Node* nextNode = node->next;

        previous->next = nextNode;
        nextNode->prev = previous;
    }

    void insert(Node* node) {
        Node* previous = right->prev;

        previous->next = node;
        node->prev = previous;

        node->next = right;
        right->prev = node;
    }

public:
    LRUCache(int capacity) : capacity(capacity) {
        left = new Node();
        right = new Node();

        left->next = right;
        right->prev = left;
    }

    int get(int key) {
        if (!cache.count(key)) {
            return -1;
        }

        Node* node = cache[key];

        remove(node);
        insert(node);

        return node->value;
    }

    void put(int key, int value) {
        if (cache.count(key)) {
            remove(cache[key]);
            delete cache[key];
        }

        Node* node = new Node(key, value);

        cache[key] = node;
        insert(node);

        if (cache.size() > capacity) {
            Node* lru = left->next;

            remove(lru);
            cache.erase(lru->key);
            delete lru;
        }
    }
};
