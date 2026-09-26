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

var minCostConnectPoints = function(points) {
    const n = points.length;
    const visited = new Array(n).fill(false);
    let visitedCount = 0;

    const minHeap = new MinHeap();
    minHeap.push([0, 0]);  // [cost, point_index]

    let totalCost = 0;

    while (visitedCount < n) {
        const [cost, u] = minHeap.pop();

        if (visited[u]) continue;

        visited[u] = true;
        visitedCount++;
        totalCost += cost;

        const [x1, y1] = points[u];

        for (let v = 0; v < n; v++) {
            if (!visited[v]) {
                const [x2, y2] = points[v];
                minHeap.push([Math.abs(x1 - x2) + Math.abs(y1 - y2), v]);
            }
        }
    }

    return totalCost;
};
