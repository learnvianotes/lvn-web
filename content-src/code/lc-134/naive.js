var canCompleteCircuit = function(gas, cost) {
    const n = gas.length;

    for (let start = 0; start < n; start++) {
        let fuel = 0;
        let possible = true;

        for (let i = 0; i < n; i++) {
            const index = (start + i) % n;
            fuel += gas[index];
            fuel -= cost[index];

            if (fuel < 0) {
                possible = false;
                break;
            }
        }

        if (possible) {
            return start;
        }
    }

    return -1;
};
