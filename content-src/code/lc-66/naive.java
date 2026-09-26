class Solution {
    public int[] plusOne(int[] digits) {
        java.math.BigInteger number = java.math.BigInteger.ZERO;

        for (int digit : digits) {
            number = number.multiply(java.math.BigInteger.TEN)
                           .add(java.math.BigInteger.valueOf(digit));
        }

        number = number.add(java.math.BigInteger.ONE);

        return number.toString().chars().map(d -> d - '0').toArray();
    }
}
