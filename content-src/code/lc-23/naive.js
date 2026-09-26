var mergeKLists = function(lists) {
    const values = [];

    for (let head of lists) {
        while (head) {
            values.push(head.val);
            head = head.next;
        }
    }

    values.sort((a, b) => a - b);

    const dummy = new ListNode();
    let current = dummy;

    for (const value of values) {
        current.next = new ListNode(value);
        current = current.next;
    }

    return dummy.next;
};
