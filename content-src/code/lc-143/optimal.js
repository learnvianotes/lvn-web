var reorderList = function(head) {
    if (!head || !head.next) {
        return;
    }

    // Find middle
    let slow = head;
    let fast = head;

    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
    }

    // Reverse second half
    let second = slow.next;
    slow.next = null;

    let previous = null;

    while (second) {
        const nextNode = second.next;
        second.next = previous;
        previous = second;
        second = nextNode;
    }

    second = previous;
    let first = head;

    // Merge
    while (second) {
        const firstNext = first.next;
        const secondNext = second.next;

        first.next = second;
        second.next = firstNext;

        first = firstNext;
        second = secondNext;
    }
};
