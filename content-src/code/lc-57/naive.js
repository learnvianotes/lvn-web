var insert = function(intervals, newInterval) {
    intervals.push(newInterval);
    intervals.sort((a, b) => a[0] - b[0] || a[1] - b[1]);

    const result = [];

    for (const [start, end] of intervals) {
        if (!result.length || start > result[result.length - 1][1]) {
            result.push([start, end]);
        } else {
            const last = result[result.length - 1];
            last[1] = Math.max(last[1], end);
        }
    }

    return result;
};
