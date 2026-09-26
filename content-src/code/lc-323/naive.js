var countComponents = function(n, edges) {
    const graph = Array.from({ length: n }, () => []);

    for (const [a, b] of edges) {
        graph[a].push(b);
        graph[b].push(a);
    }

    const visited = new Array(n).fill(false);

    const dfs = (node) => {
        visited[node] = true;

        for (const neighbor of graph[node])
            if (!visited[neighbor]) dfs(neighbor);
    };

    let components = 0;

    for (let node = 0; node < n; node++) {
        if (!visited[node]) {
            components++;
            dfs(node);
        }
    }

    return components;
};
