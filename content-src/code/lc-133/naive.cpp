class Solution {
public:
    Node* cloneGraph(Node* node) {
        if (!node) return nullptr;

        unordered_map<Node*, Node*> visited;

        function<Node*(Node*)> dfs = [&](Node* original) -> Node* {
            if (visited.count(original)) return visited[original];

            Node* clone = new Node(original->val);
            visited[original] = clone;

            for (Node* neighbor : original->neighbors)
                clone->neighbors.push_back(dfs(neighbor));

            return clone;
        };

        return dfs(node);
    }
};
