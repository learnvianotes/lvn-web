class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();

        vector<vector<int>> result(n, vector<int>(n, 0));

        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                result[c][n - 1 - r] = matrix[r][c];
            }
        }

        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                matrix[r][c] = result[r][c];
            }
        }
    }
};
