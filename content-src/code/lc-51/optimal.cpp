class Solution {
public:
    vector<vector<string>> solveNQueens(int n) {
        vector<vector<string>> result;
        vector<string> board(n, string(n, '.'));

        unordered_set<int> columns;
        unordered_set<int> positiveDiagonals;  // row + col
        unordered_set<int> negativeDiagonals;  // row - col

        function<void(int)> backtrack = [&](int row) {
            if (row == n) {
                result.push_back(board);
                return;
            }

            for (int col = 0; col < n; col++) {
                if (columns.count(col)) continue;

                if (positiveDiagonals.count(row + col)) continue;

                if (negativeDiagonals.count(row - col)) continue;

                // Place queen
                board[row][col] = 'Q';
                columns.insert(col);
                positiveDiagonals.insert(row + col);
                negativeDiagonals.insert(row - col);

                backtrack(row + 1);

                // Backtrack
                board[row][col] = '.';
                columns.erase(col);
                positiveDiagonals.erase(row + col);
                negativeDiagonals.erase(row - col);
            }
        };

        backtrack(0);

        return result;
    }
};
