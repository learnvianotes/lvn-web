class Solution {
    public int reverse(int x) {
        int sign = x < 0 ? -1 : 1;
        long value = Math.abs((long) x);  // Math.abs(Integer.MIN_VALUE) overflows int

        long reversedNum = Long.parseLong(
            new StringBuilder(String.valueOf(value)).reverse().toString()
        );
        reversedNum *= sign;

        if (reversedNum < Integer.MIN_VALUE || reversedNum > Integer.MAX_VALUE) {
            return 0;
        }

        return (int) reversedNum;
    }
}
