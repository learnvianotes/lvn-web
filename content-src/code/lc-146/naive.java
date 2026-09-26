class LRUCache {
    private int capacity;
    private Map<Integer, Integer> cache;
    private LinkedList<Integer> order;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.order = new LinkedList<>();
    }

    public int get(int key) {
        if (!cache.containsKey(key)) {
            return -1;
        }

        order.remove((Integer) key);
        order.addLast(key);

        return cache.get(key);
    }

    public void put(int key, int value) {
        if (cache.containsKey(key)) {
            order.remove((Integer) key);
        }

        cache.put(key, value);
        order.addLast(key);

        if (cache.size() > capacity) {
            int oldest = order.removeFirst();
            cache.remove(oldest);
        }
    }
}
