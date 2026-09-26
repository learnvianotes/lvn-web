class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        // Up to 100 digits overflows long, so use java.math.BigInteger (like Python's int)
        java.math.BigInteger total = toNumber(l1).add(toNumber(l2));

        if (total.signum() == 0) {
            return new ListNode(0);
        }

        ListNode dummy = new ListNode();
        ListNode current = dummy;

        while (total.signum() > 0) {
            java.math.BigInteger[] parts = total.divideAndRemainder(java.math.BigInteger.TEN);
            current.next = new ListNode(parts[1].intValue());
            total = parts[0];
            current = current.next;
        }

        return dummy.next;
    }

    private java.math.BigInteger toNumber(ListNode node) {
        java.math.BigInteger number = java.math.BigInteger.ZERO;
        java.math.BigInteger multiplier = java.math.BigInteger.ONE;

        while (node != null) {
            number = number.add(multiplier.multiply(java.math.BigInteger.valueOf(node.val)));
            multiplier = multiplier.multiply(java.math.BigInteger.TEN);
            node = node.next;
        }

        return number;
    }
}
