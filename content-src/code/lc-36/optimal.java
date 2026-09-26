class Solution {
    public boolean isValidSudoku(char[][] board) {
        List<Set<Character>> rows = new ArrayList<>(), cols = new ArrayList<>(), boxes = new ArrayList<>();
        for (int i = 0; i < 9; i++) {
            rows.add(new HashSet<>()); cols.add(new HashSet<>()); boxes.add(new HashSet<>());
        }
        for (int r = 0; r < 9; r++)
            for (int c = 0; c < 9; c++) {
                char v = board[r][c];
                if (v == '.') continue;
                int box = (r / 3) * 3 + c / 3;
                if (rows.get(r).contains(v) || cols.get(c).contains(v) || boxes.get(box).contains(v))
                    return false;
                rows.get(r).add(v); cols.get(c).add(v); boxes.get(box).add(v);
            }
        return true;
    }
}
