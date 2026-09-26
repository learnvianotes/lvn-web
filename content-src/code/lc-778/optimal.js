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

var swimInWater = function(grid) {
    const n = grid.length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    const minHeap = new MinHeap();
    minHeap.push([grid[0][0], 0, 0]);  // [time, r, c]

    const visited = Array.from({ length: n }, () => new Array(n).fill(false));
    visited[0][0] = true;

    while (minHeap.size) {
        const [time, r, c] = minHeap.pop();

        if (r === n - 1 && c === n - 1) return time;

        for (const [dr, dc] of dirs) {
            const nr = r + dr, nc = c + dc;

            if (
                nr >= 0 && nr < n &&
                nc >= 0 && nc < n &&
                !visited[nr][nc]
            ) {
                visited[nr][nc] = true;
                minHeap.push([Math.max(time, grid[nr][nc]), nr, nc]);
            }
        }
    }

    return -1;
};
