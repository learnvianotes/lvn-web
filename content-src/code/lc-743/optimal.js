class MinHeap {
    constructor() { this.heap = []; }

    get size() { return this.heap.length; }

    push(item) {
        const h = this.heap;
        h.push(item);
        let i = h.length - 1;
        while (i > 0) {
            const p = (i - 1) >> 1;
            if (h[p][0] <= h[i][0]) break;
            [h[p], h[i]] = [h[i], h[p]];
            i = p;
        }
    }

    pop() {
        const h = this.heap;
        const top = h[0];
        const last = h.pop();
        if (h.length) {
            h[0] = last;
            let i = 0;
            while (true) {
                const l = 2 * i + 1, r = l + 1;
                let m = i;
                if (l < h.length && h[l][0] < h[m][0]) m = l;
                if (r < h.length && h[r][0] < h[m][0]) m = r;
                if (m === i) break;
                [h[m], h[i]] = [h[i], h[m]];
                i = m;
            }
        }
        return top;
    }
}

var networkDelayTime = function(times, n, k) {
    const graph = Array.from({ length: n + 1 }, () => []);

    for (const [u, v, w] of times)
        graph[u].push([v, w]);

    const minHeap = new MinHeap();
    minHeap.push([0, k]);  // [time, node]

    const distances = new Map();

    while (minHeap.size) {
        const [time, node] = minHeap.pop();

        if (distances.has(node)) continue;

        distances.set(node, time);

        for (const [neighbor, weight] of graph[node])
            if (!distances.has(neighbor))
                minHeap.push([time + weight, neighbor]);
    }

    if (distances.size === n) return Math.max(...distances.values());

    return -1;
};
