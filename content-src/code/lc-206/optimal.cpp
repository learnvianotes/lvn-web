class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        ListNode* previous = nullptr;
        ListNode* current = head;

        while (current) {
            ListNode* nextNode = current->next;

            current->next = previous;

            previous = current;
            current = nextNode;
        }

        return previous;
    }
};
