class DetectSquares {
    // points[x][y] = frequency
    private Map<Integer, Map<Integer, Integer>> points;

    public DetectSquares() {
        points = new HashMap<>();
    }

    public void add(int[] point) {
        int x = point[0], y = point[1];
        points.computeIfAbsent(x, k -> new HashMap<>()).merge(y, 1, Integer::sum);
    }

    public int count(int[] point) {
        int x = point[0], y = point[1];
        int answer = 0;

        for (Map.Entry<Integer, Map<Integer, Integer>> entry : points.entrySet()) {
            int x2 = entry.getKey();
            Map<Integer, Integer> ys = entry.getValue();

            if (x2 == x) {
                continue;
            }

            int side = Math.abs(x2 - x);

            // Two possible diagonal y-coords
            for (int y2 : new int[]{y + side, y - side}) {
                if (!ys.containsKey(y2)) {
                    continue;
                }

                int cntDiag   = ys.get(y2);      // (x2, y2)
                int cntCorner = get(x, y2);      // (x,  y2)
                int cntBase   = get(x2, y);      // (x2, y )

                answer += cntDiag * cntCorner * cntBase;
            }
        }

        return answer;
    }

    private int get(int x, int y) {
        Map<Integer, Integer> ys = points.get(x);
        return ys == null ? 0 : ys.getOrDefault(y, 0);
    }
}
