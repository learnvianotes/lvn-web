var insert = function(intervals, newInterval) {
    const result = [];
    let i = 0;
    const n = intervals.length;

    // Phase 1 — completely before new interval
    while (i < n && intervals[i][1] < newInterval[0]) {
        result.push(intervals[i]);
        i++;
    }

    // Phase 2 — overlapping: merge into newInterval
    while (i < n && intervals[i][0] <= newInterval[1]) {
        newInterval[0] = Math.min(newInterval[0], intervals[i][0]);
        newInterval[1] = Math.max(newInterval[1], intervals[i][1]);
        i++;
    }

    result.push(newInterval);

    // Phase 3 — completely after new interval
    while (i < n) {
        result.push(intervals[i]);
        i++;
    }

    return result;
};
