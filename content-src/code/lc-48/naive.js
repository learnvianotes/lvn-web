var rotate = function(matrix) {
    const n = matrix.length;

    const result = Array.from({ length: n }, () => new Array(n).fill(0));

    for (let r = 0; r < n; r++) {
        for (let c = 0; c < n; c++) {
            result[c][n - 1 - r] = matrix[r][c];
        }
    }

    for (let r = 0; r < n; r++) {
        for (let c = 0; c < n; c++) {
            matrix[r][c] = result[r][c];
        }
    }
};
