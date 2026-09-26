var evalRPN = function(tokens) {
    const stack = [];
    const operators = new Set(["+", "-", "*", "/"]);
    for (const token of tokens) {
        if (!operators.has(token)) {
            stack.push(parseInt(token));
            continue;
        }
        const b = stack.pop();
        const a = stack.pop();
        let result;
        if (token === "+") result = a + b;
        else if (token === "-") result = a - b;
        else if (token === "*") result = a * b;
        else result = Math.trunc(a / b);
        stack.push(result);
    }
    return stack[stack.length - 1];
};
