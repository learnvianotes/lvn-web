class Solution {
    public boolean isSameTree(TreeNode p, TreeNode q) {
        Deque<TreeNode[]> queue = new ArrayDeque<>();
        queue.offer(new TreeNode[] { p, q });

        while (!queue.isEmpty()) {
            TreeNode[] pair = queue.poll();
            TreeNode a = pair[0], b = pair[1];

            if (a == null && b == null) continue;

            if (a == null || b == null) return false;

            if (a.val != b.val) return false;

            queue.offer(new TreeNode[] { a.left, b.left });
            queue.offer(new TreeNode[] { a.right, b.right });
        }

        return true;
    }
}
