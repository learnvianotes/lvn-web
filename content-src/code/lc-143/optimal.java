class Solution {
    public void reorderList(ListNode head) {
        if (head == null || head.next == null) {
            return;
        }

        // Find middle
        ListNode slow = head;
        ListNode fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }

        // Reverse second half
        ListNode second = slow.next;
        slow.next = null;

        ListNode previous = null;

        while (second != null) {
            ListNode nextNode = second.next;
            second.next = previous;
            previous = second;
            second = nextNode;
        }

        second = previous;
        ListNode first = head;

        // Merge
        while (second != null) {
            ListNode firstNext = first.next;
            ListNode secondNext = second.next;

            first.next = second;
            second.next = firstNext;

            first = firstNext;
            second = secondNext;
        }
    }
}
