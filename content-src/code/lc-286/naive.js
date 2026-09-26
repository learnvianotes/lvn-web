var wallsAndGates = function(rooms) {
    const INF = 2147483647;
    const rows = rooms.length;
    const cols = rooms[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    // BFS outward from one empty room until the nearest gate is found
    const nearestGate = (sr, sc) => {
        const visited = Array.from({ length: rows }, () => new Array(cols).fill(false));
        const queue = [[sr, sc, 0]];
        visited[sr][sc] = true;

        for (let head = 0; head < queue.length; head++) {
            const [r, c, dist] = queue[head];

            if (rooms[r][c] === 0) return dist;

            for (const [dr, dc] of dirs) {
                const nr = r + dr, nc = c + dc;

                if (
                    nr >= 0 && nr < rows &&
                    nc >= 0 && nc < cols &&
                    !visited[nr][nc] && rooms[nr][nc] !== -1
                ) {
                    visited[nr][nc] = true;
                    queue.push([nr, nc, dist + 1]);
                }
            }
        }

        return INF;
    };

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (rooms[r][c] === INF)
                rooms[r][c] = nearestGate(r, c);
};
