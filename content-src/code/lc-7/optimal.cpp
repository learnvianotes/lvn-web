class Solution {
public:
    int reverse(int x) {
        int sign = x < 0 ? -1 : 1;
        long long value = llabs((long long)x);  // abs(INT_MIN) overflows int

        // 64-bit result can hold any reversed 10-digit value
        long long result = 0;

        while (value) {
            int digit = value % 10;
            result = result * 10 + digit;
            value /= 10;
        }

        result *= sign;

        if (result < INT_MIN || result > INT_MAX) {
            return 0;
        }

        return (int)result;
    }
};
