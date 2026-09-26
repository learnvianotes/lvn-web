var findItinerary = function(tickets) {
    const n = tickets.length;
    const sorted = [...tickets].sort((a, b) =>
        a[0] === b[0] ? (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0)
                      : (a[0] < b[0] ? -1 : 1));

    // airport -> indices of its tickets, in lexical order of destination
    const graph = new Map();
    sorted.forEach(([src], i) => {
        if (!graph.has(src)) graph.set(src, []);
        graph.get(src).push(i);
    });

    const used = new Array(n).fill(false);
    const path = ["JFK"];

    const dfs = (airport) => {
        if (path.length === n + 1) return true;

        for (const i of graph.get(airport) || []) {
            if (used[i]) continue;

            used[i] = true;
            path.push(sorted[i][1]);

            if (dfs(sorted[i][1])) return true;

            used[i] = false;  // backtrack
            path.pop();
        }

        return false;
    };

    dfs("JFK");
    return path;
};
