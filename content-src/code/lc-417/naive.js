var pacificAtlantic = function(heights) {
    const rows = heights.length;
    const cols = heights[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    const result = [];

    const canReach = (r, c, target) => {
        const visited = new Set();

        const dfs = (x, y) => {
            if (visited.has(x * cols + y)) return false;

            if (target === "P" && (x === 0 || y === 0)) return true;
            if (target === "A" && (x === rows - 1 || y === cols - 1)) return true;

            visited.add(x * cols + y);

            for (const [dx, dy] of dirs) {
                const nx = x + dx, ny = y + dy;

                if (
                    nx >= 0 && nx < rows &&
                    ny >= 0 && ny < cols &&
                    heights[nx][ny] <= heights[x][y]
                ) {
                    if (dfs(nx, ny)) return true;
                }
            }

            return false;
        };

        return dfs(r, c);
    };

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (canReach(r, c, "P") && canReach(r, c, "A"))
                result.push([r, c]);

    return result;
};
