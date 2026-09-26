class Solution {
public:
    vector<int> countBits(int n) {
        vector<int> result;

        for (int num = 0; num <= n; num++) {
            int count = 0;
            int x = num;

            while (x) {
                x &= x - 1;
                count++;
            }

            result.push_back(count);
        }

        return result;
    }
};
