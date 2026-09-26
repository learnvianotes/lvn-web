var checkValidString = function(s) {
    const dfs = (index, balance) => {
        if (balance < 0) {
            return false;
        }

        if (index === s.length) {
            return balance === 0;
        }

        const char = s[index];

        if (char === "(") {
            return dfs(index + 1, balance + 1);
        }

        if (char === ")") {
            return dfs(index + 1, balance - 1);
        }

        // Try '*' as '(', ')', or ''
        return (
            dfs(index + 1, balance + 1) ||
            dfs(index + 1, balance - 1) ||
            dfs(index + 1, balance)
        );
    };

    return dfs(0, 0);
};
