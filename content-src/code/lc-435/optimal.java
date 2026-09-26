class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));

        int removed = 0;
        int previousEnd = Integer.MIN_VALUE;

        for (int[] interval : intervals) {
            int start = interval[0], end = interval[1];

            if (start < previousEnd) {
                removed++;
            } else {
                previousEnd = end;
            }
        }

        return removed;
    }
}
