var rotate = function(matrix) {
    const n = matrix.length;

    // Step 1 — Transpose
    for (let r = 0; r < n; r++) {
        for (let c = r + 1; c < n; c++) {
            [matrix[r][c], matrix[c][r]] = [matrix[c][r], matrix[r][c]];
        }
    }

    // Step 2 — Reverse each row
    for (const row of matrix) {
        row.reverse();
    }
};
