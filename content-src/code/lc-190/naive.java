class Solution {
    // you need treat n as an unsigned value
    public int reverseBits(int n) {
        StringBuilder binary = new StringBuilder();

        for (int i = 0; i < 32; i++) {
            binary.append(n & 1);
            n >>>= 1;
        }

        int result = 0;

        for (char bit : binary.toString().toCharArray()) {
            result = (result << 1) | (bit - '0');
        }

        return result;
    }
}
