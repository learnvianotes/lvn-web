var evalRPN = function(tokens) {
    tokens = tokens.slice();
    const operators = new Set(["+", "-", "*", "/"]);
    while (tokens.length > 1) {
        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            if (!operators.has(token)) continue;
            const a = parseInt(tokens[i - 2]), b = parseInt(tokens[i - 1]);
            let result;
            if (token === "+") result = a + b;
            else if (token === "-") result = a - b;
            else if (token === "*") result = a * b;
            else result = Math.trunc(a / b);
            tokens.splice(i - 2, 3, String(result));
            break;
        }
    }
    return parseInt(tokens[0]);
};
