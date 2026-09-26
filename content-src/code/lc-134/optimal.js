var canCompleteCircuit = function(gas, cost) {
    const sum = (arr) => arr.reduce((a, b) => a + b, 0);
    if (sum(gas) < sum(cost)) {
        return -1;
    }

    let start = 0;
    let fuel = 0;

    for (let i = 0; i < gas.length; i++) {
        fuel += gas[i] - cost[i];

        if (fuel < 0) {
            start = i + 1;
            fuel = 0;
        }
    }

    return start;
};
