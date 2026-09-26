class Solution {
    private Map<Integer, Integer> positions;
    private int[] preorder;
    private int preorderIndex;

    public TreeNode buildTree(int[] preorder, int[] inorder) {
        positions = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) positions.put(inorder[i], i);

        this.preorder = preorder;
        preorderIndex = 0;

        return build(0, inorder.length - 1);
    }

    private TreeNode build(int left, int right) {
        if (left > right) return null;

        int rootVal = preorder[preorderIndex++];

        TreeNode root = new TreeNode(rootVal);

        int mid = positions.get(rootVal);

        root.left = build(left, mid - 1);
        root.right = build(mid + 1, right);

        return root;
    }
}
