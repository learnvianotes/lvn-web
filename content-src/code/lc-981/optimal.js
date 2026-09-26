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

        let left = 0;
        let right = values.length - 1;

        let answer = "";

        while (left <= right) {
            const mid = left + Math.floor((right - left) / 2);

            if (values[mid][0] <= timestamp) {
                answer = values[mid][1];
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return answer;
    }
}
