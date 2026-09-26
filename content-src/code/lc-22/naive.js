var generateParenthesis = function(n) {
    const result = [];
    const valid = s => {
        let balance = 0;
        for (const c of s) {
            if (c === "(") balance++;
            else balance--;
            if (balance < 0) return false;
        }
        return balance === 0;
    };
    const generate = s => {
        if (s.length === 2 * n) {
            if (valid(s)) result.push(s);
            return;
        }
        generate(s + "(");
        generate(s + ")");
    };
    generate("");
    return result;
};
