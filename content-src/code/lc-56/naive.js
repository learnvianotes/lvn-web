var merge = function(input) {
    let intervals = input.map((x) => [...x]);
    let changed = true;

    while (changed) {
        changed = false;
        const result = [];
        const used = new Array(intervals.length).fill(false);

        for (let i = 0; i < intervals.length; i++) {
            if (used[i]) continue;

            let current = intervals[i];

            for (let j = i + 1; j < intervals.length; j++) {
                if (used[j]) continue;

                const other = intervals[j];

                if (current[0] <= other[1] && other[0] <= current[1]) {
                    current = [
                        Math.min(current[0], other[0]),
                        Math.max(current[1], other[1]),
                    ];
                    used[j] = true;
                    changed = true;
                }
            }

            result.push(current);
        }

        intervals = result;
    }

    return intervals;
};
