class Solution {
public:
    uint32_t reverseBits(uint32_t n) {
        string binary = "";

        for (int i = 0; i < 32; i++) {
            binary += to_string(n & 1);
            n >>= 1;
        }

        uint32_t result = 0;

        for (char bit : binary) {
            result = (result << 1) | (bit - '0');
        }

        return result;
    }
};
