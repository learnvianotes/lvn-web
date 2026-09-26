class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        List<ListNode> nodes = new ArrayList<>();

        ListNode current = head;

        while (current != null) {
            nodes.add(current);
            current = current.next;
        }

        int n = nodes.size();

        for (int start = 0; start < n; start += k) {
            int end = Math.min(start + k, n);

            if (end - start < k) {
                break;
            }

            Collections.reverse(nodes.subList(start, end));
        }

        for (int i = 0; i + 1 < n; i++) {
            nodes.get(i).next = nodes.get(i + 1);
        }

        if (!nodes.isEmpty()) {
            nodes.get(n - 1).next = null;
        }

        return nodes.isEmpty() ? null : nodes.get(0);
    }
}
