class Solution {
    public int[][] insert(int[][] intervals, int[] newInterval) {
        List<int[]> all = new ArrayList<>(Arrays.asList(intervals));
        all.add(newInterval);
        all.sort((a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1]));

        List<int[]> result = new ArrayList<>();

        for (int[] interval : all) {
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
