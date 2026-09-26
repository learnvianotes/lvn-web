class Codec {
public:
    // Encodes a tree to a single string.
    string serialize(TreeNode* root) {
        string result;
        dfsSerialize(root, result);
        result.pop_back();  // drop trailing comma
        return result;
    }

    // Decodes your encoded data to tree.
    TreeNode* deserialize(string data) {
        vector<string> values;
        stringstream ss(data);
        string token;
        while (getline(ss, token, ',')) values.push_back(token);

        int index = 0;
        return dfsDeserialize(values, index);
    }

private:
    void dfsSerialize(TreeNode* node, string& result) {
        if (!node) {
            result += "#,";
            return;
        }

        result += to_string(node->val) + ",";
        dfsSerialize(node->left, result);
        dfsSerialize(node->right, result);
    }

    TreeNode* dfsDeserialize(vector<string>& values, int& index) {
        if (values[index] == "#") {
            index++;
            return nullptr;
        }

        TreeNode* node = new TreeNode(stoi(values[index]));
        index++;

        node->left = dfsDeserialize(values, index);
        node->right = dfsDeserialize(values, index);

        return node;
    }
};
