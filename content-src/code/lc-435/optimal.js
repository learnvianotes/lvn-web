var eraseOverlapIntervals = function(intervals) {
    intervals.sort((a, b) => a[1] - b[1]);

    let removed = 0;
    let previousEnd = -Infinity;

    for (const [start, end] of intervals) {
        if (start < previousEnd) {
            removed++;
        } else {
            previousEnd = end;
        }
    }

    return removed;
};
