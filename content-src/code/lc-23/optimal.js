var mergeKLists = function(lists) {
    // Minimal binary min-heap of nodes keyed by val
    const heap = [];

    const push = (node) => {
        heap.push(node);
        let i = heap.length - 1;
        while (i > 0) {
            const parent = (i - 1) >> 1;
            if (heap[parent].val <= heap[i].val) break;
            [heap[parent], heap[i]] = [heap[i], heap[parent]];
            i = parent;
        }
    };

    const pop = () => {
        const top = heap[0];
        const last = heap.pop();
        if (heap.length) {
            heap[0] = last;
            let i = 0;
            while (true) {
                const l = 2 * i + 1, r = l + 1;
                let smallest = i;
                if (l < heap.length && heap[l].val < heap[smallest].val) smallest = l;
                if (r < heap.length && heap[r].val < heap[smallest].val) smallest = r;
                if (smallest === i) break;
                [heap[smallest], heap[i]] = [heap[i], heap[smallest]];
                i = smallest;
            }
        }
        return top;
    };

    for (const node of lists) {
        if (node) {
            push(node);
        }
    }

    const dummy = new ListNode();
    let current = dummy;

    while (heap.length) {
        const node = pop();

        current.next = node;
        current = current.next;

        if (node.next) {
            push(node.next);
        }
    }

    return dummy.next;
};
