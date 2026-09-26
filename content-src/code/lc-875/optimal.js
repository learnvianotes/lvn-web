var minEatingSpeed = function(piles, h) {
    let left = 1;
    let right = Math.max(...piles);

    let answer = right;

    while (left <= right) {
        const speed = left + Math.floor((right - left) / 2);

        let hours = 0;

        for (const pile of piles) {
            hours += Math.floor((pile + speed - 1) / speed);
        }

        if (hours <= h) {
            answer = speed;
            right = speed - 1;
        } else {
            left = speed + 1;
        }
    }

    return answer;
};
