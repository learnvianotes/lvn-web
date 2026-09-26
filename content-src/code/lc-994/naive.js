var orangesRotting = function(grid) {
    const rows = grid.length;
    const cols = grid[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    let minutes = 0;

    // Each minute, rescan the whole grid and rot neighbours of rotten oranges
    while (true) {
        let changed = false;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (grid[r][c] !== 2) continue;

                for (const [dr, dc] of dirs) {
                    const nr = r + dr, nc = c + dc;

                    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] === 1) {
                        grid[nr][nc] = 3;  // rots this minute, spreads next minute
                        changed = true;
                    }
                }
            }
        }

        if (!changed) break;

        for (const row of grid)
            for (let c = 0; c < cols; c++)
                if (row[c] === 3) row[c] = 2;

        minutes++;
    }

    for (const row of grid)
        if (row.includes(1)) return -1;

    return minutes;
};
