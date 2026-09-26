class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {
        int length = 0;
        ListNode* current = head;

        while (current) {
            length++;
            current = current->next;
        }

        ListNode dummy(0, head);
        current = &dummy;

        for (int i = 0; i < length - n; i++) {
            current = current->next;
        }

        current->next = current->next->next;

        return dummy.next;
    }
};
