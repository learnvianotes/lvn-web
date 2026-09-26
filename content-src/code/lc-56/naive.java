class Solution {
    public int[][] merge(int[][] input) {
        List<int[]> intervals = new ArrayList<>();
        for (int[] interval : input) intervals.add(interval.clone());

        boolean changed = true;

        while (changed) {
            changed = false;
            List<int[]> result = new ArrayList<>();
            boolean[] used = new boolean[intervals.size()];

            for (int i = 0; i < intervals.size(); i++) {
                if (used[i]) continue;

                int[] current = intervals.get(i);

                for (int j = i + 1; j < intervals.size(); j++) {
                    if (used[j]) continue;

                    int[] other = intervals.get(j);

                    if (current[0] <= other[1] && other[0] <= current[1]) {
                        current = new int[]{
                            Math.min(current[0], other[0]),
                            Math.max(current[1], other[1]),
                        };
                        used[j] = true;
                        changed = true;
                    }
                }

                result.add(current);
            }

            intervals = result;
        }

        return intervals.toArray(new int[0][]);
    }
}
