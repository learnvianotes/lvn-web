class Solution {
    public boolean canAttendMeetings(List<Interval> intervals) {
        int n = intervals.size();

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int start1 = intervals.get(i).start, end1 = intervals.get(i).end;
                int start2 = intervals.get(j).start, end2 = intervals.get(j).end;

                if (start1 < end2 && start2 < end1) return false;
            }
        }

        return true;
    }
}
