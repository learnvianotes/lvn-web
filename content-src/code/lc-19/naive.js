var removeNthFromEnd = function(head, n) {
    let length = 0;
    let current = head;

    while (current) {
        length++;
        current = current.next;
    }

    const dummy = new ListNode(0, head);
    current = dummy;

    for (let i = 0; i < length - n; i++) {
        current = current.next;
    }

    current.next = current.next.next;

    return dummy.next;
};
