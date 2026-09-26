var spiralOrder = function(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const visited = Array.from({ length: rows }, () => new Array(cols).fill(false));
    const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];
    const result = [];
    let r = 0, c = 0, direction = 0;

    for (let step = 0; step < rows * cols; step++) {
        result.push(matrix[r][c]);
        visited[r][c] = true;

        let nr = r + directions[direction][0];
        let nc = c + directions[direction][1];

        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols || visited[nr][nc]) {
            direction = (direction + 1) % 4;
            nr = r + directions[direction][0];
            nc = c + directions[direction][1];
        }

        r = nr;
        c = nc;
    }

    return result;
};
