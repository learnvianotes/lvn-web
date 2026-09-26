class Solution {
    public Node copyRandomList(Node head) {
        if (head == null) {
            return null;
        }

        Map<Node, Node> copies = new HashMap<>();

        Node current = head;

        while (current != null) {
            copies.put(current, new Node(current.val));
            current = current.next;
        }

        current = head;

        while (current != null) {
            copies.get(current).next = copies.get(current.next);
            copies.get(current).random = copies.get(current.random);

            current = current.next;
        }

        return copies.get(head);
    }
}
