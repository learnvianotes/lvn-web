var validTree = function(n, edges) {
    if (edges.length !== n - 1) return false;

    const parent = Array.from({ length: n }, (_, i) => i);
    const rank = new Array(n).fill(1);

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

    for (const [a, b] of edges)
        if (!union(a, b)) return false;

    return true;
};
