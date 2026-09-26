var canAttendMeetings = function(intervals) {
    const n = intervals.length;

    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            const { start: start1, end: end1 } = intervals[i];
            const { start: start2, end: end2 } = intervals[j];

            if (start1 < end2 && start2 < end1) return false;
        }
    }

    return true;
};
