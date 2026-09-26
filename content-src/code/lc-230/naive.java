class Solution {
    public int kthSmallest(TreeNode root, int k) {
        List<Integer> values = new ArrayList<>();
        inorder(root, values);

        return values.get(k - 1);
    }

    private void inorder(TreeNode node, List<Integer> values) {
        if (node == null) return;

        inorder(node.left, values);
        values.add(node.val);
        inorder(node.right, values);
    }
}
