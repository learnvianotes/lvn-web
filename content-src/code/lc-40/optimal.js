var combinationSum2 = function(candidates, target) {
    candidates.sort((a, b) => a - b);
    const result = [];

    const backtrack = (start, remaining, current) => {
        if (remaining === 0) {
            result.push([...current]);
            return;
        }

        for (let i = start; i < candidates.length; i++) {
            // Skip duplicate choices at the same level
            if (i > start && candidates[i] === candidates[i - 1]) continue;

            // Since sorted, no later value can work
            if (candidates[i] > remaining) break;

            current.push(candidates[i]);

            // i + 1 because each element can be used once
            backtrack(i + 1, remaining - candidates[i], current);

            current.pop();
        }
    };

    backtrack(0, target, []);
    return result;
};
