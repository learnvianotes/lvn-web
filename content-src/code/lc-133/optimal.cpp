class Solution {
public:
    Node* cloneGraph(Node* node) {
        if (!node) return nullptr;

        unordered_map<Node*, Node*> clones;
        clones[node] = new Node(node->val);

        queue<Node*> q;
        q.push(node);

        while (!q.empty()) {
            Node* current = q.front();
            q.pop();

            for (Node* neighbor : current->neighbors) {
                if (!clones.count(neighbor)) {
                    clones[neighbor] = new Node(neighbor->val);
                    q.push(neighbor);
                }

                clones[current]->neighbors.push_back(clones[neighbor]);
            }
        }

        return clones[node];
    }
};
