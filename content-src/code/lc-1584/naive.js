var minCostConnectPoints = function(points) {
    const n = points.length;

    // Build every edge [dist, i, j] and sort them
    const edges = [];
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            const dist = Math.abs(points[i][0] - points[j][0]) + Math.abs(points[i][1] - points[j][1]);
            edges.push([dist, i, j]);
        }
    }
    edges.sort((a, b) => a[0] - b[0]);

    const parent = Array.from({ length: n }, (_, i) => i);

    const find = (x) => {
        while (x !== parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    };

    let totalCost = 0, used = 0;

    for (const [dist, i, j] of edges) {
        const rootI = find(i), rootJ = find(j);
        if (rootI === rootJ) continue;

        parent[rootI] = rootJ;
        totalCost += dist;

        if (++used === n - 1) break;
    }

    return totalCost;
};
