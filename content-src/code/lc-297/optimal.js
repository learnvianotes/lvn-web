var serialize = function(root) {
    const result = [];

    const dfs = (node) => {
        if (!node) {
            result.push("#");
            return;
        }

        result.push(String(node.val));
        dfs(node.left);
        dfs(node.right);
    };

    dfs(root);
    return result.join(",");
};

var deserialize = function(data) {
    const values = data.split(",");
    let index = 0;

    const dfs = () => {
        if (values[index] === "#") {
            index++;
            return null;
        }

        const node = new TreeNode(Number(values[index]));
        index++;

        node.left = dfs();
        node.right = dfs();

        return node;
    };

    return dfs();
};
