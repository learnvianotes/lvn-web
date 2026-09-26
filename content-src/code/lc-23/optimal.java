class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> heap = new PriorityQueue<>((a, b) -> Integer.compare(a.val, b.val));

        for (ListNode node : lists) {
            if (node != null) {
                heap.offer(node);
            }
        }

        ListNode dummy = new ListNode();
        ListNode current = dummy;

        while (!heap.isEmpty()) {
            ListNode node = heap.poll();

            current.next = node;
            current = current.next;

            if (node.next != null) {
                heap.offer(node.next);
            }
        }

        return dummy.next;
    }
}
