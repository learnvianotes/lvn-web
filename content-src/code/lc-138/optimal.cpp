class Solution {
public:
    Node* copyRandomList(Node* head) {
        if (!head) {
            return nullptr;
        }

        Node* current = head;

        // Create copied nodes
        while (current) {
            Node* copy = new Node(current->val);

            copy->next = current->next;
            current->next = copy;

            current = copy->next;
        }

        // Set random pointers
        current = head;

        while (current) {
            if (current->random) {
                current->next->random = current->random->next;
            }

            current = current->next->next;
        }

        // Separate lists
        Node dummy(0);
        Node* copyCurrent = &dummy;
        current = head;

        while (current) {
            Node* copy = current->next;

            copyCurrent->next = copy;
            copyCurrent = copy;

            current->next = copy->next;
            current = current->next;
        }

        return dummy.next;
    }
};
