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

class MedianFinder {
    constructor() {
        this.small = new MinHeap((a, b) => b - a);  // max-heap
        this.large = new MinHeap((a, b) => a - b);  // min-heap
    }

    addNum(num) {
        this.small.push(num);

        // Ensure every small <= every large
        if (this.small.size() && this.large.size() && this.small.peek() > this.large.peek()) {
            this.large.push(this.small.pop());
        }

        // Balance sizes
        if (this.small.size() > this.large.size() + 1) {
            this.large.push(this.small.pop());
        } else if (this.large.size() > this.small.size()) {
            this.small.push(this.large.pop());
        }
    }

    findMedian() {
        if (this.small.size() > this.large.size()) return this.small.peek();

        return (this.small.peek() + this.large.peek()) / 2;
    }
}
