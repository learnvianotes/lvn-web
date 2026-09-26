var isValid = function(s) {
    const stack = [];
    const pairs = { ")": "(", "]": "[", "}": "{" };
    for (const c of s) {
        if ("([{".includes(c)) {
            stack.push(c);
        } else {
            if (!stack.length) return false;
            if (stack.pop() !== pairs[c]) return false;
        }
    }
    return stack.length === 0;
};
