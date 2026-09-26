var combinationSum2 = function(candidates, target) {
    const result = new Map();  // key -> combination, acts as a set
    candidates.sort((a, b) => a - b);

    const backtrack = (index, remaining, current) => {
        if (remaining === 0) {
            result.set(current.join(','), [...current]);
            return;
        }

        if (index === candidates.length || remaining < 0) return;

        // Don't choose
        backtrack(index + 1, remaining, current);

        // Choose
        current.push(candidates[index]);
        backtrack(index + 1, remaining - candidates[index], current);
        current.pop();
    };

    backtrack(0, target, []);
    return [...result.values()];
};
