var copyRandomList = function(head) {
    if (!head) {
        return null;
    }

    const copies = new Map();

    let current = head;

    while (current) {
        copies.set(current, new _Node(current.val, null, null));
        current = current.next;
    }

    current = head;

    while (current) {
        copies.get(current).next = copies.get(current.next) || null;
        copies.get(current).random = copies.get(current.random) || null;

        current = current.next;
    }

    return copies.get(head);
};
