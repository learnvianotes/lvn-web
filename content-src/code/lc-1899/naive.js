var mergeTriplets = function(triplets, target) {
    const n = triplets.length;

    const dfs = (index, current) => {
        if (current.every((v, i) => v === target[i])) {
            return true;
        }

        if (index === n) {
            return false;
        }

        if (dfs(index + 1, current)) {
            return true;
        }

        const triplet = triplets[index];

        if (triplet.every((v, i) => v <= target[i])) {
            const merged = current.map((v, i) => Math.max(v, triplet[i]));

            if (dfs(index + 1, merged)) {
                return true;
            }
        }

        return false;
    };

    return dfs(0, [0, 0, 0]);
};
