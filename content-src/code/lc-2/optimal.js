var addTwoNumbers = function(l1, l2) {
    const dummy = new ListNode();
    let current = dummy;

    let carry = 0;

    while (l1 || l2 || carry) {
        const a = l1 ? l1.val : 0;
        const b = l2 ? l2.val : 0;

        const total = a + b + carry;

        carry = Math.floor(total / 10);

        current.next = new ListNode(total % 10);

        current = current.next;

        if (l1) l1 = l1.next;
        if (l2) l2 = l2.next;
    }

    return dummy.next;
};
