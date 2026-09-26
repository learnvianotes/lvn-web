var mergeTriplets = function(triplets, target) {
    const found = [false, false, false];

    for (const triplet of triplets) {
        if (triplet.some((v, i) => v > target[i])) {
            continue;
        }

        for (let i = 0; i < 3; i++) {
            if (triplet[i] === target[i]) {
                found[i] = true;
            }
        }
    }

    return found.every(Boolean);
};
