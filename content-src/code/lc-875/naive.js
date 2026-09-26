var minEatingSpeed = function(piles, h) {
    const maxPile = Math.max(...piles);

    for (let speed = 1; speed <= maxPile; speed++) {
        let hours = 0;

        for (const pile of piles) {
            hours += Math.floor((pile + speed - 1) / speed);
        }

        if (hours <= h) {
            return speed;
        }
    }

    return maxPile;
};
