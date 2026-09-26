var removeNthFromEnd = function(head, n) {
    const dummy = new ListNode(0, head);

    let slow = dummy;
    let fast = dummy;

    for (let i = 0; i < n; i++) {
        fast = fast.next;
    }

    while (fast.next) {
        slow = slow.next;
        fast = fast.next;
    }

    slow.next = slow.next.next;

    return dummy.next;
};
