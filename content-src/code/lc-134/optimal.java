class Solution {
    public int canCompleteCircuit(int[] gas, int[] cost) {
        long totalGas = 0, totalCost = 0;
        for (int i = 0; i < gas.length; i++) {
            totalGas += gas[i];
            totalCost += cost[i];
        }
        if (totalGas < totalCost) {
            return -1;
        }

        int start = 0;
        int fuel = 0;

        for (int i = 0; i < gas.length; i++) {
            fuel += gas[i] - cost[i];

            if (fuel < 0) {
                start = i + 1;
                fuel = 0;
            }
        }

        return start;
    }
}
