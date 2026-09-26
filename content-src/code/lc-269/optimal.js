var alienOrder = function(words) {
    const graph = new Map();
    for (const word of words)
        for (const c of word)
            if (!graph.has(c)) graph.set(c, new Set());

    for (let i = 0; i + 1 < words.length; i++) {
        const w1 = words[i], w2 = words[i + 1];
        const minLength = Math.min(w1.length, w2.length);

        if (w1.length > w2.length && w1.startsWith(w2)) return "";

        for (let j = 0; j < minLength; j++) {
            if (w1[j] !== w2[j]) {
                graph.get(w1[j]).add(w2[j]);
                break;
            }
        }
    }

    // true = on the current path (cycle), false = finished
    const visited = new Map();
    const result = [];

    const dfs = (c) => {
        if (visited.has(c)) return visited.get(c);

        visited.set(c, true);

        for (const neighbor of graph.get(c))
            if (dfs(neighbor)) return true;

        visited.set(c, false);
        result.push(c);

        return false;
    };

    for (const c of graph.keys())
        if (dfs(c)) return "";

    return result.reverse().join("");
};
