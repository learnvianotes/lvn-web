class Solution {
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
        vector<int> values;

        while (list1) {
            values.push_back(list1->val);
            list1 = list1->next;
        }

        while (list2) {
            values.push_back(list2->val);
            list2 = list2->next;
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
