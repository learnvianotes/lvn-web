var maxAreaOfIsland = function(grid) {
    const rows = grid.length;
    const cols = grid[0].length;

    const visited = Array.from({ length: rows }, () => new Array(cols).fill(false));

    const dfs = (r, c) => {
        if (
            r < 0 || r >= rows ||
            c < 0 || c >= cols ||
            grid[r][c] === 0 || visited[r][c]
        ) return 0;

        visited[r][c] = true;

        return 1 + dfs(r + 1, c) + dfs(r - 1, c)
                 + dfs(r, c + 1) + dfs(r, c - 1);
    };

    let answer = 0;

    for (let r = 0; r < rows; r++)
        for (let c = 0; c < cols; c++)
            if (grid[r][c] === 1 && !visited[r][c])
                answer = Math.max(answer, dfs(r, c));

    return answer;
};
