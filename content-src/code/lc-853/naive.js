var carFleet = function(target, position, speed) {
    const cars = position.map((p, i) => [p, speed[i]]).sort((a, b) => a[0] - b[0]);
    const fleets = [];
    for (const [pos, spd] of cars) {
        const time = (target - pos) / spd;
        while (fleets.length && fleets[fleets.length - 1] <= time) fleets.pop();
        fleets.push(time);
    }
    return fleets.length;
};
