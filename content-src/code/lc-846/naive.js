var isNStraightHand = function(hand, groupSize) {
    if (hand.length % groupSize !== 0) {
        return false;
    }

    hand.sort((a, b) => a - b);

    while (hand.length > 0) {
        const first = hand[0];

        for (let value = first; value < first + groupSize; value++) {
            const index = hand.indexOf(value);
            if (index === -1) {
                return false;
            }

            hand.splice(index, 1);
        }
    }

    return true;
};
