class Solution {
    public boolean isValidBST(TreeNode root) {
        return check(root);
    }

    private long minValue(TreeNode node) {
        if (node == null) return Long.MAX_VALUE;
        return Math.min(node.val, Math.min(minValue(node.left), minValue(node.right)));
    }

    private long maxValue(TreeNode node) {
        if (node == null) return Long.MIN_VALUE;
        return Math.max(node.val, Math.max(maxValue(node.left), maxValue(node.right)));
    }

    private boolean check(TreeNode node) {
        if (node == null) return true;

        long leftMax = maxValue(node.left);
        long rightMin = minValue(node.right);

        if (node.val <= leftMax || node.val >= rightMin) return false;

        return check(node.left) && check(node.right);
    }
}
