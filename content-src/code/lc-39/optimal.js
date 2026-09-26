var combinationSum = function(candidates, target) {
    const result = [];
    candidates.sort((a, b) => a - b);

    const backtrack = (start, remaining, current) => {
        if (remaining === 0) {
            result.push([...current]);
            return;
        }

        for (let i = start; i < candidates.length; i++) {
            const num = candidates[i];

            if (num > remaining) break;

            current.push(num);

            // i, not i + 1, because we can reuse the same number
            backtrack(i, remaining - num, current);

            current.pop();
        }
    };

    backtrack(0, target, []);
    return result;
};
