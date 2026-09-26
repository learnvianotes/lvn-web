class Solution {
    public boolean isSubtree(TreeNode root, TreeNode subRoot) {
        StringBuilder textBuilder = new StringBuilder();
        StringBuilder patternBuilder = new StringBuilder();
        serialize(root, textBuilder);
        serialize(subRoot, patternBuilder);
        String text = textBuilder.toString();
        String pattern = patternBuilder.toString();

        // KMP algorithm
        int m = pattern.length();
        int[] lps = new int[m];

        int j = 0;
        for (int i = 1; i < m; i++) {
            while (j > 0 && pattern.charAt(i) != pattern.charAt(j)) j = lps[j - 1];

            if (pattern.charAt(i) == pattern.charAt(j)) j++;

            lps[i] = j;
        }

        j = 0;

        for (int i = 0; i < text.length(); i++) {
            while (j > 0 && text.charAt(i) != pattern.charAt(j)) j = lps[j - 1];

            if (text.charAt(i) == pattern.charAt(j)) j++;

            if (j == m) return true;
        }

        return false;
    }

    private void serialize(TreeNode node, StringBuilder out) {
        if (node == null) {
            out.append('#');
            return;
        }

        out.append(',').append(node.val);
        serialize(node.left, out);
        serialize(node.right, out);
    }
}
