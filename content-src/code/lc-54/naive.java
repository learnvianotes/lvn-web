class Solution {
    public List<Integer> spiralOrder(int[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        boolean[][] visited = new boolean[rows][cols];
        int[][] directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        List<Integer> result = new ArrayList<>();
        int r = 0, c = 0, direction = 0;

        for (int step = 0; step < rows * cols; step++) {
            result.add(matrix[r][c]);
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
}
