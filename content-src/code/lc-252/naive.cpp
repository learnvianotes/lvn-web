class Solution {
public:
    bool canAttendMeetings(vector<Interval>& intervals) {
        int n = intervals.size();

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int start1 = intervals[i].start, end1 = intervals[i].end;
                int start2 = intervals[j].start, end2 = intervals[j].end;

                if (start1 < end2 && start2 < end1) return false;
            }
        }

        return true;
    }
};
