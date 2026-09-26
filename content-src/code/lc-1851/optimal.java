class Solution {
    public int[] minInterval(int[][] intervals, int[] queries) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));

        Integer[] sortedQueries = new Integer[queries.length];  // original indices, sorted by query
        for (int i = 0; i < queries.length; i++) sortedQueries[i] = i;
        Arrays.sort(sortedQueries, (a, b) -> Integer.compare(queries[a], queries[b]));

        int[] result = new int[queries.length];
        Arrays.fill(result, -1);

        // min-heap of {size, end}
        PriorityQueue<int[]> heap = new PriorityQueue<>(
            (a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1])
        );
        int i = 0;

        for (int originalIndex : sortedQueries) {
            int query = queries[originalIndex];

            // Add all intervals whose start <= query
            while (i < intervals.length && intervals[i][0] <= query) {
                int start = intervals[i][0], end = intervals[i][1];
                int size = end - start + 1;
                heap.offer(new int[]{size, end});
                i++;
            }

            // Remove intervals that ended before this query
            while (!heap.isEmpty() && heap.peek()[1] < query) heap.poll();

            if (!heap.isEmpty()) result[originalIndex] = heap.peek()[0];
        }

        return result;
    }
}
