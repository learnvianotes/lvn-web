var setZeroes = function(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;

    const firstRowZero = matrix[0].some((v) => v === 0);
    const firstColZero = matrix.some((row) => row[0] === 0);

    // Use first row/col as markers
    for (let r = 1; r < rows; r++) {
        for (let c = 1; c < cols; c++) {
            if (matrix[r][c] === 0) {
                matrix[r][0] = 0;
                matrix[0][c] = 0;
            }
        }
    }

    // Zero marked rows
    for (let r = 1; r < rows; r++) {
        if (matrix[r][0] === 0) {
            for (let c = 1; c < cols; c++) {
                matrix[r][c] = 0;
            }
        }
    }

    // Zero marked columns
    for (let c = 1; c < cols; c++) {
        if (matrix[0][c] === 0) {
            for (let r = 1; r < rows; r++) {
                matrix[r][c] = 0;
            }
        }
    }

    // Handle first row and column
    if (firstRowZero) {
        for (let c = 0; c < cols; c++) {
            matrix[0][c] = 0;
        }
    }

    if (firstColZero) {
        for (let r = 0; r < rows; r++) {
            matrix[r][0] = 0;
        }
    }
};
