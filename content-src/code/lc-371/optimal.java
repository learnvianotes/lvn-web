class Solution {
    public int getSum(int a, int b) {
        // Java ints are already 32-bit two's complement, so no MASK is needed
        while (b != 0) {
            int carry = (a & b) << 1;
            a = a ^ b;
            b = carry;
        }

        return a;
    }
}
