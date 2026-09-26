class Solution {
public:
    void solve(vector<vector<char>>& board) {
        int rows = board.size(), cols = board[0].size();
        vector<vector<bool>> visited;

        // Can this 'O' reach the border through other 'O's?
        function<bool(int, int)> reachesBorder = [&](int r, int c) -> bool {
            if (r < 0 || r >= rows || c < 0 || c >= cols) return true;
            if (board[r][c] != 'O' || visited[r][c]) return false;

            visited[r][c] = true;

            return reachesBorder(r + 1, c) || reachesBorder(r - 1, c) ||
                   reachesBorder(r, c + 1) || reachesBorder(r, c - 1);
        };

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (board[r][c] != 'O') continue;

                visited.assign(rows, vector<bool>(cols, false));

                if (!reachesBorder(r, c)) board[r][c] = 'X';
            }
        }
    }
};
