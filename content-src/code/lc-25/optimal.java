class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        ListNode dummy = new ListNode(0, head);
        ListNode groupPrev = dummy;

        while (true) {
            ListNode kth = getKth(groupPrev, k);

            if (kth == null) {
                break;
            }

            ListNode groupNext = kth.next;

            // Reverse group
            ListNode previous = groupNext;
            ListNode current = groupPrev.next;

            while (current != groupNext) {
                ListNode nextNode = current.next;

                current.next = previous;

                previous = current;
                current = nextNode;
            }

            ListNode oldStart = groupPrev.next;

            groupPrev.next = kth;
            groupPrev = oldStart;
        }

        return dummy.next;
    }

    private ListNode getKth(ListNode node, int k) {
        while (node != null && k > 0) {
            node = node.next;
            k--;
        }

        return node;
    }
}
