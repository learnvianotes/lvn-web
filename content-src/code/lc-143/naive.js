var reorderList = function(head) {
    const nodes = [];

    let current = head;

    while (current) {
        nodes.push(current);
        current = current.next;
    }

    let left = 0;
    let right = nodes.length - 1;

    while (left < right) {
        nodes[left].next = nodes[right];
        left++;

        if (left === right) {
            break;
        }

        nodes[right].next = nodes[left];
        right--;
    }

    nodes[left].next = null;
};
