var networkDelayTime = function(times, n, k) {
    const dist = new Array(n + 1).fill(Infinity);
    dist[k] = 0;

    // Relax every edge n - 1 times
    for (let i = 0; i < n - 1; i++) {
        for (const [u, v, w] of times) {
            if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;
        }
    }

    let answer = 0;
    for (let node = 1; node <= n; node++) {
        if (dist[node] === Infinity) return -1;
        answer = Math.max(answer, dist[node]);
    }

    return answer;
};
