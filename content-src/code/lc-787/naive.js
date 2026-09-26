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

var findCheapestPrice = function(n, flights, src, dst, k) {
    const graph = Array.from({ length: n }, () => []);
    for (const [u, v, price] of flights)
        graph[u].push([v, price]);

    // [cost, node, flights taken] - no visited set, so states can repeat
    const minHeap = new MinHeap();
    minHeap.push([0, src, 0]);

    while (minHeap.size) {
        const [cost, node, used] = minHeap.pop();

        if (node === dst) return cost;
        if (used > k) continue;  // at most k stops = k + 1 flights

        for (const [next, price] of graph[node])
            minHeap.push([cost + price, next, used + 1]);
    }

    return -1;
};
