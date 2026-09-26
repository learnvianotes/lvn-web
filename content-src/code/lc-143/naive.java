class Solution {
    public void reorderList(ListNode head) {
        List<ListNode> nodes = new ArrayList<>();

        ListNode current = head;

        while (current != null) {
            nodes.add(current);
            current = current.next;
        }

        int left = 0;
        int right = nodes.size() - 1;

        while (left < right) {
            nodes.get(left).next = nodes.get(right);
            left++;

            if (left == right) {
                break;
            }

            nodes.get(right).next = nodes.get(left);
            right--;
        }

        nodes.get(left).next = null;
    }
}
