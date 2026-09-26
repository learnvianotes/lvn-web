class Solution {
public:
    void reorderList(ListNode* head) {
        if (!head || !head->next) {
            return;
        }

        // Find middle
        ListNode* slow = head;
        ListNode* fast = head;

        while (fast && fast->next) {
            slow = slow->next;
            fast = fast->next->next;
        }

        // Reverse second half
        ListNode* second = slow->next;
        slow->next = nullptr;

        ListNode* previous = nullptr;

        while (second) {
            ListNode* nextNode = second->next;
            second->next = previous;
            previous = second;
            second = nextNode;
        }

        second = previous;
        ListNode* first = head;

        // Merge
        while (second) {
            ListNode* firstNext = first->next;
            ListNode* secondNext = second->next;

            first->next = second;
            second->next = firstNext;

            first = firstNext;
            second = secondNext;
        }
    }
};
