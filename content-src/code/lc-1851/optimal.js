class MinHeap {
    constructor(compare = (a, b) => a - b, items = []) {
        this.compare = compare;
        this.data = items;
        for (let i = (items.length >> 1) - 1; i >= 0; i--) this.siftDown(i);
    }

    size() { return this.data.length; }

    peek() { return this.data[0]; }

    push(value) {
        const data = this.data;
        data.push(value);
        let i = data.length - 1;
        while (i > 0) {
            const parent = (i - 1) >> 1;
            if (this.compare(data[i], data[parent]) >= 0) break;
            [data[i], data[parent]] = [data[parent], data[i]];
            i = parent;
        }
    }

    pop() {
        const data = this.data;
        const top = data[0];
        const last = data.pop();
        if (data.length > 0) {
            data[0] = last;
            this.siftDown(0);
        }
        return top;
    }

    siftDown(i) {
        const data = this.data;
        while (true) {
            const left = 2 * i + 1, right = left + 1;
            let smallest = i;
            if (left < data.length && this.compare(data[left], data[smallest]) < 0) smallest = left;
            if (right < data.length && this.compare(data[right], data[smallest]) < 0) smallest = right;
            if (smallest === i) return;
            [data[i], data[smallest]] = [data[smallest], data[i]];
            i = smallest;
        }
    }
}

var minInterval = function(intervals, queries) {
    intervals.sort((a, b) => a[0] - b[0] || a[1] - b[1]);

    const sortedQueries = queries
        .map((query, i) => [query, i])
        .sort((a, b) => a[0] - b[0] || a[1] - b[1]);

    const result = new Array(queries.length).fill(-1);
    const heap = new MinHeap((a, b) => a[0] - b[0] || a[1] - b[1]);  // [size, end]
    let i = 0;

    for (const [query, originalIndex] of sortedQueries) {
        // Add all intervals whose start <= query
        while (i < intervals.length && intervals[i][0] <= query) {
            const [start, end] = intervals[i];
            const size = end - start + 1;
            heap.push([size, end]);
            i++;
        }

        // Remove intervals that ended before this query
        while (heap.size() && heap.peek()[1] < query) heap.pop();

        if (heap.size()) result[originalIndex] = heap.peek()[0];
    }

    return result;
};
