var pacificAtlantic = function(heights) {
    const rows = heights.length;
    const cols = heights[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    const bfs = (starts) => {
        const visited = Array.from({ length: rows }, () => new Array(cols).fill(false));
        const queue = [];

        for (const [r, c] of starts) {
            visited[r][c] = true;
            queue.push([r, c]);
        }

        for (let head = 0; head < queue.length; head++) {
            const [r, c] = queue[head];

            for (const [dr, dc] of dirs) {
                const nr = r + dr, nc = c + dc;

                if (
                    nr >= 0 && nr < rows &&
                    nc >= 0 && nc < cols &&
                    !visited[nr][nc] &&
                    heights[nr][nc] >= heights[r][c]
                ) {
                    visited[nr][nc] = true;
                    queue.push([nr, nc]);
                }
            }
        }

        return visited;
    };

    const pacific = [];
    for (let r = 0; r < rows; r++) pacific.push([r, 0]);
    for (let c = 0; c < cols; c++) pacific.push([0, c]);

    const atlantic = [];
    for (let r = 0; r < rows; r++) atlantic.push([r, cols - 1]);
    for (let c = 0; c < cols; c++) atlantic.push([rows - 1, c]);

    const p = bfs(pacific);
    const a = bfs(atlantic);

    const result = [];

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (p[r][c] && a[r][c])
                result.push([r, c]);

    return result;
};
