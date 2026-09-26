var reverseKGroup = function(head, k) {
    const getKth = (node, k) => {
        while (node && k > 0) {
            node = node.next;
            k--;
        }

        return node;
    };

    const dummy = new ListNode(0, head);
    let groupPrev = dummy;

    while (true) {
        const kth = getKth(groupPrev, k);

        if (!kth) {
            break;
        }

        const groupNext = kth.next;

        // Reverse group
        let previous = groupNext;
        let current = groupPrev.next;

        while (current !== groupNext) {
            const nextNode = current.next;

            current.next = previous;

            previous = current;
            current = nextNode;
        }

        const oldStart = groupPrev.next;

        groupPrev.next = kth;
        groupPrev = oldStart;
    }

    return dummy.next;
};
