class DLLNode {
    constructor(key = 0, value = 0) {
        this.key = key;
        this.value = value;
        this.prev = null;
        this.next = null;
    }
}

class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();

        this.left = new DLLNode();
        this.right = new DLLNode();

        this.left.next = this.right;
        this.right.prev = this.left;
    }

    remove(node) {
        const previous = node.prev;
        const nextNode = node.next;

        previous.next = nextNode;
        nextNode.prev = previous;
    }

    insert(node) {
        const previous = this.right.prev;

        previous.next = node;
        node.prev = previous;

        node.next = this.right;
        this.right.prev = node;
    }

    get(key) {
        if (!this.cache.has(key)) {
            return -1;
        }

        const node = this.cache.get(key);

        this.remove(node);
        this.insert(node);

        return node.value;
    }

    put(key, value) {
        if (this.cache.has(key)) {
            this.remove(this.cache.get(key));
        }

        const node = new DLLNode(key, value);

        this.cache.set(key, node);
        this.insert(node);

        if (this.cache.size > this.capacity) {
            const lru = this.left.next;

            this.remove(lru);
            this.cache.delete(lru.key);
        }
    }
}
