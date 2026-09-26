class LRUCache {
    private static class Node {
        int key, value;
        Node prev, next;

        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private int capacity;
    private Map<Integer, Node> cache;
    private Node left;
    private Node right;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();

        this.left = new Node(0, 0);
        this.right = new Node(0, 0);

        left.next = right;
        right.prev = left;
    }

    private void remove(Node node) {
        Node previous = node.prev;
        Node nextNode = node.next;

        previous.next = nextNode;
        nextNode.prev = previous;
    }

    private void insert(Node node) {
        Node previous = right.prev;

        previous.next = node;
        node.prev = previous;

        node.next = right;
        right.prev = node;
    }

    public int get(int key) {
        if (!cache.containsKey(key)) {
            return -1;
        }

        Node node = cache.get(key);

        remove(node);
        insert(node);

        return node.value;
    }

    public void put(int key, int value) {
        if (cache.containsKey(key)) {
            remove(cache.get(key));
        }

        Node node = new Node(key, value);

        cache.put(key, node);
        insert(node);

        if (cache.size() > capacity) {
            Node lru = left.next;

            remove(lru);
            cache.remove(lru.key);
        }
    }
}
