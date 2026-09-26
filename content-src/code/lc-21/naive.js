var mergeTwoLists = function(list1, list2) {
    const values = [];

    while (list1) {
        values.push(list1.val);
        list1 = list1.next;
    }

    while (list2) {
        values.push(list2.val);
        list2 = list2.next;
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
