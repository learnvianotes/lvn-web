var wallsAndGates = function(rooms) {
    const rows = rooms.length;
    const cols = rooms[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    const queue = [];

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (rooms[r][c] === 0) queue.push([r, c]);

    for (let head = 0; head < queue.length; head++) {
        const [r, c] = queue[head];

        for (const [dr, dc] of dirs) {
            const nr = r + dr, nc = c + dc;

            if (
                nr >= 0 && nr < rows &&
                nc >= 0 && nc < cols &&
                rooms[nr][nc] === 2147483647
            ) {
                rooms[nr][nc] = rooms[r][c] + 1;
                queue.push([nr, nc]);
            }
        }
    }
};
