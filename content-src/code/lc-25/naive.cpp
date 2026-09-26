class Solution {
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        vector<ListNode*> nodes;

        ListNode* current = head;

        while (current) {
            nodes.push_back(current);
            current = current->next;
        }

        int n = nodes.size();

        for (int start = 0; start < n; start += k) {
            int end = min(start + k, n);

            if (end - start < k) {
                break;
            }

            reverse(nodes.begin() + start, nodes.begin() + end);
        }

        for (int i = 0; i + 1 < n; i++) {
            nodes[i]->next = nodes[i + 1];
        }

        if (!nodes.empty()) {
            nodes.back()->next = nullptr;
        }

        return nodes.empty() ? nullptr : nodes[0];
    }
};
