var isNStraightHand = function(hand, groupSize) {
    if (hand.length % groupSize !== 0) {
        return false;
    }

    const count = new Map();
    for (const card of hand) {
        count.set(card, (count.get(card) || 0) + 1);
    }

    const keys = [...count.keys()].sort((a, b) => a - b);

    for (const first of keys) {
        if (count.get(first) === 0) {
            continue;
        }

        const frequency = count.get(first);

        for (let value = first; value < first + groupSize; value++) {
            if ((count.get(value) || 0) < frequency) {
                return false;
            }

            count.set(value, count.get(value) - frequency);
        }
    }

    return true;
};
