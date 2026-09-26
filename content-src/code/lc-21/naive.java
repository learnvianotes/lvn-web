class Solution {
    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {
        List<Integer> values = new ArrayList<>();

        while (list1 != null) {
            values.add(list1.val);
            list1 = list1.next;
        }

        while (list2 != null) {
            values.add(list2.val);
            list2 = list2.next;
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
