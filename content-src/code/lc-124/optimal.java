class Solution {
    private int answer;

    public int maxPathSum(TreeNode root) {
        answer = Integer.MIN_VALUE;
        dfs(root);
        return answer;
    }

    private int dfs(TreeNode node) {
        if (node == null) return 0;

        int left = Math.max(0, dfs(node.left));
        int right = Math.max(0, dfs(node.right));

        int current = node.val + left + right;

        answer = Math.max(answer, current);

        return node.val + Math.max(left, right);
    }
}
