class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int longestIncreasingPath(int[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int answer = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                answer = Math.max(answer, dfs(matrix, r, c));
            }
        }

        return answer;
    }

    private int dfs(int[][] matrix, int r, int c) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int best = 1;

        for (int[] d : DIRS) {
            int nr = r + d[0], nc = c + d[1];

            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                && matrix[nr][nc] > matrix[r][c]) {
                best = Math.max(best, 1 + dfs(matrix, nr, nc));
            }
        }

        return best;
    }
}
