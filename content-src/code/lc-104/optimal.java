class Solution {
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;

        Deque<TreeNode> queue = new ArrayDeque<>();
        queue.offer(root);
        int depth = 0;

        while (!queue.isEmpty()) {
            for (int i = queue.size(); i > 0; i--) {
                TreeNode node = queue.poll();

                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }

            depth++;
        }

        return depth;
    }
}
