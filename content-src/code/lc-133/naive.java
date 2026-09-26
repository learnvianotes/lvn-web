class Solution {
    private Map<Node, Node> visited = new HashMap<>();

    public Node cloneGraph(Node node) {
        if (node == null) return null;
        return dfs(node);
    }

    private Node dfs(Node original) {
        if (visited.containsKey(original)) return visited.get(original);

        Node clone = new Node(original.val);
        visited.put(original, clone);

        for (Node neighbor : original.neighbors)
            clone.neighbors.add(dfs(neighbor));

        return clone;
    }
}
