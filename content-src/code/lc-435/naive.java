class Solution {
    private int best;

    public int eraseOverlapIntervals(int[][] intervals) {
        best = intervals.length;
        dfs(intervals, 0, new ArrayList<>());
        return best;
    }

    private boolean overlaps(int[] a, int[] b) {
        return a[0] < b[1] && b[0] < a[1];
    }

    private void dfs(int[][] intervals, int index, List<int[]> chosen) {
        int n = intervals.length;

        if (index == n) {
            best = Math.min(best, n - chosen.size());
            return;
        }

        // Skip this interval
        dfs(intervals, index + 1, chosen);

        // Take if compatible
        boolean compatible = true;
        for (int[] x : chosen) {
            if (overlaps(intervals[index], x)) {
                compatible = false;
                break;
            }
        }

        if (compatible) {
            chosen.add(intervals[index]);
            dfs(intervals, index + 1, chosen);
            chosen.remove(chosen.size() - 1);
        }
    }
}
