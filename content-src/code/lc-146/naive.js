class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();
        this.order = [];
    }

    get(key) {
        if (!this.cache.has(key)) {
            return -1;
        }

        this.order.splice(this.order.indexOf(key), 1);
        this.order.push(key);

        return this.cache.get(key);
    }

    put(key, value) {
        if (this.cache.has(key)) {
            this.order.splice(this.order.indexOf(key), 1);
        }

        this.cache.set(key, value);
        this.order.push(key);

        if (this.cache.size > this.capacity) {
            const oldest = this.order.shift();
            this.cache.delete(oldest);
        }
    }
}
