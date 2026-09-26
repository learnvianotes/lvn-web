var minInterval = function(intervals, queries) {
    const result = [];

    for (const query of queries) {
        let best = Infinity;

        for (const [start, end] of intervals) {
            if (start <= query && query <= end) {
                const size = end - start + 1;
                best = Math.min(best, size);
            }
        }

        result.push(best === Infinity ? -1 : best);
    }

    return result;
};
