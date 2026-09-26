class Solution {
    public int goodNodes(TreeNode root) {
        return dfs(root, new ArrayList<>());
    }

    private int dfs(TreeNode node, List<Integer> path) {
        if (node == null) return 0;

        path.add(node.val);

        int count = 0;
        if (node.val == Collections.max(path)) count++;

        count += dfs(node.left, path);
        count += dfs(node.right, path);

        path.remove(path.size() - 1);
        return count;
    }
}
