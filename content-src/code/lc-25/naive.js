var reverseKGroup = function(head, k) {
    const nodes = [];

    let current = head;

    while (current) {
        nodes.push(current);
        current = current.next;
    }

    for (let start = 0; start < nodes.length; start += k) {
        const end = Math.min(start + k, nodes.length);

        if (end - start < k) {
            break;
        }

        nodes.splice(start, k, ...nodes.slice(start, end).reverse());
    }

    for (let i = 0; i < nodes.length - 1; i++) {
        nodes[i].next = nodes[i + 1];
    }

    if (nodes.length) {
        nodes[nodes.length - 1].next = null;
    }

    return nodes.length ? nodes[0] : null;
};
