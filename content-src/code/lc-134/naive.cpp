class Solution {
public:
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        int n = gas.size();

        for (int start = 0; start < n; start++) {
            int fuel = 0;
            bool possible = true;

            for (int i = 0; i < n; i++) {
                int index = (start + i) % n;
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
    }
};
