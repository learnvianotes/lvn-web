class Solution {
public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        vector<int> values;

        for (ListNode* head : lists) {
            while (head) {
                values.push_back(head->val);
                head = head->next;
            }
        }

        sort(values.begin(), values.end());

        ListNode dummy;
        ListNode* current = &dummy;

        for (int value : values) {
            current->next = new ListNode(value);
            current = current->next;
        }

        return dummy.next;
    }
};
