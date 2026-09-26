var searchMatrix = function(matrix, target) {
    for (const row of matrix) {
        for (const value of row) {
            if (value === target) {
                return true;
            }
        }
    }

    return false;
};
