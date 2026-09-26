class Solution {
    public int maxPathSum(TreeNode root) {
        return path(root);
    }

    private int gain(TreeNode node) {
        if (node == null) return 0;

        return node.val + Math.max(0, Math.max(gain(node.left), gain(node.right)));
    }

    private int path(TreeNode node) {
        if (node == null) return Integer.MIN_VALUE;

        int left = gain(node.left);
        int right = gain(node.right);

        int current = node.val + Math.max(0, left) + Math.max(0, right);

        return Math.max(current, Math.max(path(node.left), path(node.right)));
    }
}
