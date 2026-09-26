class TimeMap {
    constructor() {
        this.store = new Map();
    }

    set(key, value, timestamp) {
        if (!this.store.has(key)) {
            this.store.set(key, []);
        }

        this.store.get(key).push([timestamp, value]);
    }

    get(key, timestamp) {
        if (!this.store.has(key)) {
            return "";
        }

        const values = this.store.get(key);

        for (let i = values.length - 1; i >= 0; i--) {
            if (values[i][0] <= timestamp) {
                return values[i][1];
            }
        }

        return "";
    }
}
