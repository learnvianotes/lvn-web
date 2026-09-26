class DetectSquares {
    private Map<List<Integer>, Integer> points;

    public DetectSquares() {
        points = new HashMap<>();
    }

    public void add(int[] point) {
        points.merge(Arrays.asList(point[0], point[1]), 1, Integer::sum);
    }

    public int count(int[] point) {
        int x = point[0], y = point[1];
        int answer = 0;

        for (Map.Entry<List<Integer>, Integer> entry : points.entrySet()) {
            int x2 = entry.getKey().get(0);
            int y2 = entry.getKey().get(1);
            int cntDiag = entry.getValue();

            if (x2 == x || y2 == y) {
                continue;
            }

            if (Math.abs(x2 - x) != Math.abs(y2 - y)) {
                continue;
            }

            answer += cntDiag
                * points.getOrDefault(Arrays.asList(x2, y), 0)
                * points.getOrDefault(Arrays.asList(x, y2), 0);
        }

        return answer;
    }
}
