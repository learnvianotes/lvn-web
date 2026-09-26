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

var leastInterval = function(tasks, n) {
    const count = new Map();
    for (const task of tasks) count.set(task, (count.get(task) || 0) + 1);

    const heap = new MinHeap((a, b) => b - a, [...count.values()]);  // max-heap

    const cooldown = [];  // [remaining, time it becomes available]
    let head = 0;

    let time = 0;

    while (heap.size() > 0 || head < cooldown.length) {
        time++;

        // Add tasks whose cooldown is over
        while (head < cooldown.length && cooldown[head][1] === time) {
            heap.push(cooldown[head][0]);
            head++;
        }

        if (heap.size() > 0) {
            const freq = heap.pop() - 1;

            if (freq !== 0) cooldown.push([freq, time + n + 1]);
        }
    }

    return time;
};
