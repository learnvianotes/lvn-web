var swimInWater = function(grid) {
    const n = grid.length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    // Can we reach the corner using only cells with height <= t?
    const canReach = (t) => {
        if (grid[0][0] > t) return false;

        const visited = Array.from({ length: n }, () => new Array(n).fill(false));
        const queue = [[0, 0]];
        visited[0][0] = true;

        for (let head = 0; head < queue.length; head++) {
            const [r, c] = queue[head];

            if (r === n - 1 && c === n - 1) return true;

            for (const [dr, dc] of dirs) {
                const nr = r + dr, nc = c + dc;

                if (
                    nr >= 0 && nr < n &&
                    nc >= 0 && nc < n &&
                    !visited[nr][nc] && grid[nr][nc] <= t
                ) {
                    visited[nr][nc] = true;
                    queue.push([nr, nc]);
                }
            }
        }

        return false;
    };

    let lo = 0, hi = n * n - 1;

    while (lo < hi) {
        const mid = (lo + hi) >> 1;

        if (canReach(mid)) hi = mid;
        else lo = mid + 1;
    }

    return lo;
};
