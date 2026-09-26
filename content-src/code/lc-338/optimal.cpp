class Solution {
public:
    vector<int> countBits(int n) {
        vector<int> result(n + 1, 0);

        for (int num = 1; num <= n; num++) {
            result[num] = result[num >> 1] + (num & 1);
        }

        return result;
    }
};
