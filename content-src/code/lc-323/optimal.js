var countComponents = function(n, edges) {
    const parent = Array.from({ length: n }, (_, i) => i);
    const rank = new Array(n).fill(1);
    let components = n;

    const find = (x) => {
        while (x !== parent[x]) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    };

    const union = (a, b) => {
        let rootA = find(a), rootB = find(b);

        if (rootA === rootB) return;

        if (rank[rootA] < rank[rootB]) [rootA, rootB] = [rootB, rootA];

        parent[rootB] = rootA;
        rank[rootA] += rank[rootB];

        components--;
    };

    for (const [a, b] of edges) union(a, b);

    return components;
};
