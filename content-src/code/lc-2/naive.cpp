class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        // Up to 100 digits overflows any built-in integer (Python has big ints),
        // so each number is kept as a digit string, least significant digit first.
        auto toNumber = [](ListNode* node) {
            string number;

            while (node) {
                number += char('0' + node->val);
                node = node->next;
            }

            return number;
        };

        string a = toNumber(l1);
        string b = toNumber(l2);

        string total;
        int carry = 0;

        for (int i = 0; i < max(a.size(), b.size()) || carry; i++) {
            int digit = carry;
            if (i < a.size()) digit += a[i] - '0';
            if (i < b.size()) digit += b[i] - '0';

            total += char('0' + digit % 10);
            carry = digit / 10;
        }

        ListNode dummy;
        ListNode* current = &dummy;

        for (char digit : total) {
            current->next = new ListNode(digit - '0');
            current = current->next;
        }

        return dummy.next;
    }
};
