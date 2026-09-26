class Solution {
public:
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        long long totalGas = accumulate(gas.begin(), gas.end(), 0LL);
        long long totalCost = accumulate(cost.begin(), cost.end(), 0LL);
        if (totalGas < totalCost) {
            return -1;
        }

        int start = 0;
        int fuel = 0;

        for (int i = 0; i < (int)gas.size(); i++) {
            fuel += gas[i] - cost[i];

            if (fuel < 0) {
                start = i + 1;
                fuel = 0;
            }
        }

        return start;
    }
};
