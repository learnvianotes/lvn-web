class Solution {
    public TreeNode buildTree(int[] preorder, int[] inorder) {
        if (preorder.length == 0 || inorder.length == 0) return null;

        int rootVal = preorder[0];
        TreeNode root = new TreeNode(rootVal);

        int index = 0;
        while (inorder[index] != rootVal) index++;

        root.left = buildTree(
            Arrays.copyOfRange(preorder, 1, index + 1),
            Arrays.copyOfRange(inorder, 0, index)
        );

        root.right = buildTree(
            Arrays.copyOfRange(preorder, index + 1, preorder.length),
            Arrays.copyOfRange(inorder, index + 1, inorder.length)
        );

        return root;
    }
}
