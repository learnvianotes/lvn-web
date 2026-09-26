var findRedundantConnection = function(edges) {
    const n = edges.length;
    const parent = Array.from({ length: n + 1 }, (_, i) => i);
    const rank = new Array(n + 1).fill(1);

    const find = (x) => {
        while (x !== parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    };

    const union = (a, b) => {
        let rootA = find(a), rootB = find(b);

        if (rootA === rootB) return false;

        if (rank[rootA] < rank[rootB]) [rootA, rootB] = [rootB, rootA];

        parent[rootB] = rootA;
        rank[rootA] += rank[rootB];

        return true;
    };

    for (const [u, v] of edges)
        if (!union(u, v)) return [u, v];

    return [];
};
