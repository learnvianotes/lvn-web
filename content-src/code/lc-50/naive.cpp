class Solution {
public:
    double myPow(double x, int n) {
        long long N = n;  // -n overflows int when n == INT_MIN
        if (N < 0) {
            x = 1 / x;
            N = -N;
        }

        double result = 1;

        for (long long i = 0; i < N; i++) {
            result *= x;
        }

        return result;
    }
};
