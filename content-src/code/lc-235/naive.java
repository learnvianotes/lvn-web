class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        List<TreeNode> pPath = pathTo(root, p);
        List<TreeNode> qPath = pathTo(root, q);

        TreeNode answer = root;

        for (int i = 0; i < Math.min(pPath.size(), qPath.size()); i++) {
            if (pPath.get(i) != qPath.get(i)) break;
            answer = pPath.get(i);
        }

        return answer;
    }

    private List<TreeNode> pathTo(TreeNode node, TreeNode target) {
        List<TreeNode> path = new ArrayList<>();

        while (node != null) {
            path.add(node);

            if (target.val < node.val) node = node.left;
            else if (target.val > node.val) node = node.right;
            else break;
        }

        return path;
    }
}
