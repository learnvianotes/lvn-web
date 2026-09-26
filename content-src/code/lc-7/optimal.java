class Solution {
    public int reverse(int x) {
        int sign = x < 0 ? -1 : 1;
        long value = Math.abs((long) x);  // Math.abs(Integer.MIN_VALUE) overflows int

        // 64-bit result can hold any reversed 10-digit value
        long result = 0;

        while (value != 0) {
            long digit = value % 10;
            result = result * 10 + digit;
            value /= 10;
        }

        result *= sign;

        if (result < Integer.MIN_VALUE || result > Integer.MAX_VALUE) {
            return 0;
        }

        return (int) result;
    }
}
