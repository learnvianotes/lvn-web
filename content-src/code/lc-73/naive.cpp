class Solution {
public:
    void setZeroes(vector<vector<int>>& matrix) {
        unordered_set<int> rows;
        unordered_set<int> cols;

        for (int r = 0; r < (int)matrix.size(); r++) {
            for (int c = 0; c < (int)matrix[0].size(); c++) {
                if (matrix[r][c] == 0) {
                    rows.insert(r);
                    cols.insert(c);
                }
            }
        }

        for (int r : rows) {
            for (int c = 0; c < (int)matrix[0].size(); c++) {
                matrix[r][c] = 0;
            }
        }

        for (int c : cols) {
            for (int r = 0; r < (int)matrix.size(); r++) {
                matrix[r][c] = 0;
            }
        }
    }
};
