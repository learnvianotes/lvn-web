var eraseOverlapIntervals = function(intervals) {
    const n = intervals.length;
    let best = n;

    const overlaps = (a, b) => a[0] < b[1] && b[0] < a[1];

    const dfs = (index, chosen) => {
        if (index === n) {
            best = Math.min(best, n - chosen.length);
            return;
        }

        // Skip this interval
        dfs(index + 1, chosen);

        // Take if compatible
        if (chosen.every((x) => !overlaps(intervals[index], x))) {
            chosen.push(intervals[index]);
            dfs(index + 1, chosen);
            chosen.pop();
        }
    };

    dfs(0, []);
    return best;
};
