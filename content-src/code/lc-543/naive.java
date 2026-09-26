class Solution {
    public int diameterOfBinaryTree(TreeNode root) {
        if (root == null) return 0;

        int leftDiameter = diameterOfBinaryTree(root.left);
        int rightDiameter = diameterOfBinaryTree(root.right);

        int current = height(root.left) + height(root.right);

        return Math.max(current, Math.max(leftDiameter, rightDiameter));
    }

    private int height(TreeNode node) {
        if (node == null) return 0;
        return 1 + Math.max(height(node.left), height(node.right));
    }
}
