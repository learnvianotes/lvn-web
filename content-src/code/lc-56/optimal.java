class Solution {
    public int[][] merge(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1]));
        List<int[]> result = new ArrayList<>();

        for (int[] interval : intervals) {
            int start = interval[0], end = interval[1];

            if (result.isEmpty() || start > result.get(result.size() - 1)[1]) {
                result.add(new int[]{start, end});
            } else {
                int[] last = result.get(result.size() - 1);
                last[1] = Math.max(last[1], end);
            }
        }

        return result.toArray(new int[0][]);
    }
}
