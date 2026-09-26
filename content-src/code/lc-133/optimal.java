class Solution {
    public Node cloneGraph(Node node) {
        if (node == null) return null;

        Map<Node, Node> clones = new HashMap<>();
        clones.put(node, new Node(node.val));

        Deque<Node> queue = new ArrayDeque<>();
        queue.offer(node);

        while (!queue.isEmpty()) {
            Node current = queue.poll();

            for (Node neighbor : current.neighbors) {
                if (!clones.containsKey(neighbor)) {
                    clones.put(neighbor, new Node(neighbor.val));
                    queue.offer(neighbor);
                }

                clones.get(current).neighbors.add(clones.get(neighbor));
            }
        }

        return clones.get(node);
    }
}
