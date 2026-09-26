var addTwoNumbers = function(l1, l2) {
    // Up to 100 digits exceeds Number precision, so use BigInt
    const toNumber = (node) => {
        let number = 0n;
        let multiplier = 1n;

        while (node) {
            number += BigInt(node.val) * multiplier;
            multiplier *= 10n;
            node = node.next;
        }

        return number;
    };

    let total = toNumber(l1) + toNumber(l2);

    const dummy = new ListNode();
    let current = dummy;

    if (total === 0n) {
        return new ListNode(0);
    }

    while (total) {
        current.next = new ListNode(Number(total % 10n));
        total /= 10n;
        current = current.next;
    }

    return dummy.next;
};
