class Solution {
public:
    int getSum(int a, int b) {
        // uint32_t wraps at 32 bits, doing the job of Python's MASK
        uint32_t x = a;
        uint32_t y = b;

        while (y != 0) {
            uint32_t carry = (x & y) << 1;
            x = x ^ y;
            y = carry;
        }

        // Reinterpret the 32-bit pattern as a signed int
        return (int)x;
    }
};
