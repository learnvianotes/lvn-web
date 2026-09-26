var orangesRotting = function(grid) {
    const rows = grid.length;
    const cols = grid[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    let queue = [];
    let fresh = 0;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === 2) queue.push([r, c]);
            else if (grid[r][c] === 1) fresh++;
        }
    }

    let minutes = 0;

    while (queue.length && fresh) {
        const next = [];

        for (const [r, c] of queue) {
            for (const [dr, dc] of dirs) {
                const nr = r + dr, nc = c + dc;

                if (
                    nr >= 0 && nr < rows &&
                    nc >= 0 && nc < cols &&
                    grid[nr][nc] === 1
                ) {
                    grid[nr][nc] = 2;
                    fresh--;
                    next.push([nr, nc]);
                }
            }
        }

        queue = next;
        minutes++;
    }

    return fresh === 0 ? minutes : -1;
};
