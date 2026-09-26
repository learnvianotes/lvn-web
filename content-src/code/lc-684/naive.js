var findRedundantConnection = function(edges) {
    const n = edges.length;
    const graph = Array.from({ length: n + 1 }, () => []);
    let visited;

    // Is there already a path from u to v?
    const connected = (u, v) => {
        if (u === v) return true;

        visited[u] = true;

        for (const next of graph[u])
            if (!visited[next] && connected(next, v)) return true;

        return false;
    };

    for (const [u, v] of edges) {
        visited = new Array(n + 1).fill(false);

        if (connected(u, v)) return [u, v];  // this edge closes a cycle

        graph[u].push(v);
        graph[v].push(u);
    }

    return [];
};
