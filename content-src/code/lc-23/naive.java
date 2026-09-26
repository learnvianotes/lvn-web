class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        List<Integer> values = new ArrayList<>();

        for (ListNode head : lists) {
            while (head != null) {
                values.add(head.val);
                head = head.next;
            }
        }

        Collections.sort(values);

        ListNode dummy = new ListNode();
        ListNode current = dummy;

        for (int value : values) {
            current.next = new ListNode(value);
            current = current.next;
        }

        return dummy.next;
    }
}
