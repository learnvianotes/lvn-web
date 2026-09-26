class Solution {
public:
    int longestIncreasingPath(vector<vector<int>>& matrix) {
        int rows = matrix.size();
        int cols = matrix[0].size();

        memo.assign(rows, vector<int>(cols, 0));
        int answer = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                answer = max(answer, dfs(matrix, r, c));
            }
        }

        return answer;
    }

private:
    int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    vector<vector<int>> memo;

    int dfs(vector<vector<int>>& matrix, int r, int c) {
        if (memo[r][c]) return memo[r][c];

        int rows = matrix.size();
        int cols = matrix[0].size();
        int best = 1;

        for (auto& d : dirs) {
            int nr = r + d[0], nc = c + d[1];

            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                && matrix[nr][nc] > matrix[r][c]) {
                best = max(best, 1 + dfs(matrix, nr, nc));
            }
        }

        memo[r][c] = best;
        return best;
    }
};
