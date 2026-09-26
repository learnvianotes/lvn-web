public class Codec {
    private String[] values;
    private int index;

    // Encodes a tree to a single string.
    public String serialize(TreeNode root) {
        List<String> result = new ArrayList<>();
        dfsSerialize(root, result);
        return String.join(",", result);
    }

    // Decodes your encoded data to tree.
    public TreeNode deserialize(String data) {
        values = data.split(",");
        index = 0;
        return dfsDeserialize();
    }

    private void dfsSerialize(TreeNode node, List<String> result) {
        if (node == null) {
            result.add("#");
            return;
        }

        result.add(String.valueOf(node.val));
        dfsSerialize(node.left, result);
        dfsSerialize(node.right, result);
    }

    private TreeNode dfsDeserialize() {
        if (values[index].equals("#")) {
            index++;
            return null;
        }

        TreeNode node = new TreeNode(Integer.parseInt(values[index]));
        index++;

        node.left = dfsDeserialize();
        node.right = dfsDeserialize();

        return node;
    }
}
