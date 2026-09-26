class Solution {
public:
    Node* copyRandomList(Node* head) {
        if (!head) {
            return nullptr;
        }

        unordered_map<Node*, Node*> copies;
        copies[nullptr] = nullptr;

        Node* current = head;

        while (current) {
            copies[current] = new Node(current->val);
            current = current->next;
        }

        current = head;

        while (current) {
            copies[current]->next = copies[current->next];
            copies[current]->random = copies[current->random];

            current = current->next;
        }

        return copies[head];
    }
};
