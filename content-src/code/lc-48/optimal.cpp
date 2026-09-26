class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();

        // Step 1 — Transpose
        for (int r = 0; r < n; r++) {
            for (int c = r + 1; c < n; c++) {
                swap(matrix[r][c], matrix[c][r]);
            }
        }

        // Step 2 — Reverse each row
        for (auto& row : matrix) {
            reverse(row.begin(), row.end());
        }
    }
};
