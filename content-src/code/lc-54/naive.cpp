class Solution {
public:
    vector<int> spiralOrder(vector<vector<int>>& matrix) {
        int rows = matrix.size();
        int cols = matrix[0].size();
        vector<vector<bool>> visited(rows, vector<bool>(cols, false));
        int directions[4][2] = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        vector<int> result;
        int r = 0, c = 0, direction = 0;

        for (int step = 0; step < rows * cols; step++) {
            result.push_back(matrix[r][c]);
            visited[r][c] = true;

            int nr = r + directions[direction][0];
            int nc = c + directions[direction][1];

            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols || visited[nr][nc]) {
                direction = (direction + 1) % 4;
                nr = r + directions[direction][0];
                nc = c + directions[direction][1];
            }

            r = nr;
            c = nc;
        }

        return result;
    }
};
