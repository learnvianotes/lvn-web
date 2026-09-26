class Solution {
public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        using Entry = tuple<int, int, ListNode*>;
        priority_queue<Entry, vector<Entry>, greater<Entry>> heap;

        for (int i = 0; i < lists.size(); i++) {
            if (lists[i]) {
                heap.push({lists[i]->val, i, lists[i]});
            }
        }

        ListNode dummy;
        ListNode* current = &dummy;

        while (!heap.empty()) {
            auto [value, i, node] = heap.top();
            heap.pop();

            current->next = node;
            current = current->next;

            if (node->next) {
                heap.push({node->next->val, i, node->next});
            }
        }

        return dummy.next;
    }
};
