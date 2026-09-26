class Solution {
    public double myPow(double x, int n) {
        long N = n;  // -n overflows int when n == Integer.MIN_VALUE
        if (N < 0) {
            x = 1 / x;
            N = -N;
        }

        double result = 1;

        for (long i = 0; i < N; i++) {
            result *= x;
        }

        return result;
    }
}
