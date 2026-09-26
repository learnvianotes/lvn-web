var copyRandomList = function(head) {
    if (!head) {
        return null;
    }

    let current = head;

    // Create copied nodes
    while (current) {
        const copy = new _Node(current.val, null, null);

        copy.next = current.next;
        current.next = copy;

        current = copy.next;
    }

    // Set random pointers
    current = head;

    while (current) {
        if (current.random) {
            current.next.random = current.random.next;
        }

        current = current.next.next;
    }

    // Separate lists
    const dummy = new _Node(0, null, null);
    let copyCurrent = dummy;
    current = head;

    while (current) {
        const copy = current.next;

        copyCurrent.next = copy;
        copyCurrent = copy;

        current.next = copy.next;
        current = current.next;
    }

    return dummy.next;
};
