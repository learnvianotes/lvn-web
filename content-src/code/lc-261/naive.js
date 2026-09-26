var validTree = function(n, edges) {
    if (edges.length !== n - 1) return false;

    const graph = Array.from({ length: n }, () => []);

    for (const [a, b] of edges) {
        graph[a].push(b);
        graph[b].push(a);
    }

    const visited = new Set();

    const dfs = (node, parent) => {
        if (visited.has(node)) return false;

        visited.add(node);

        for (const neighbor of graph[node]) {
            if (neighbor === parent) continue;
            if (!dfs(neighbor, node)) return false;
        }

        return true;
    };

    return dfs(0, -1) && visited.size === n;
};
