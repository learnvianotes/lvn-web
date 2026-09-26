class Solution {
    public int[] minInterval(int[][] intervals, int[] queries) {
        int[] result = new int[queries.length];

        for (int q = 0; q < queries.length; q++) {
            int query = queries[q];
            int best = Integer.MAX_VALUE;

            for (int[] interval : intervals) {
                int start = interval[0], end = interval[1];

                if (start <= query && query <= end) {
                    int size = end - start + 1;
                    best = Math.min(best, size);
                }
            }

            result[q] = best == Integer.MAX_VALUE ? -1 : best;
        }

        return result;
    }
}
