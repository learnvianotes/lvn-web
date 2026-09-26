var maxAreaOfIsland = function(grid) {
    const rows = grid.length;
    const cols = grid[0].length;

    const dfs = (r, c) => {
        if (
            r < 0 || r >= rows ||
            c < 0 || c >= cols ||
            grid[r][c] === 0
        ) return 0;

        grid[r][c] = 0;

        return 1 + dfs(r + 1, c) + dfs(r - 1, c)
                 + dfs(r, c + 1) + dfs(r, c - 1);
    };

    let answer = 0;

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (grid[r][c] === 1)
                answer = Math.max(answer, dfs(r, c));

    return answer;
};
