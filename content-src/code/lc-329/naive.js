var longestIncreasingPath = function(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];

    const dfs = (r, c) => {
        let best = 1;

        for (const [dr, dc] of dirs) {
            const nr = r + dr, nc = c + dc;

            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                && matrix[nr][nc] > matrix[r][c]) {
                best = Math.max(best, 1 + dfs(nr, nc));
            }
        }

        return best;
    };

    let answer = 0;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            answer = Math.max(answer, dfs(r, c));
        }
    }

    return answer;
};
