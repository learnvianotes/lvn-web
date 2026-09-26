var hasCycle = function(head) {
    const visited = new Set();

    while (head) {
        if (visited.has(head)) {
            return true;
        }

        visited.add(head);
        head = head.next;
    }

    return false;
};
