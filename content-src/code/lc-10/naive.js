var isMatch = function(s, p) {
    const dfs = (i, j) => {
        if (j === p.length) return i === s.length;

        const firstMatch = i < s.length && (p[j] === s[i] || p[j] === ".");

        if (j + 1 < p.length && p[j + 1] === "*") {
            return dfs(i, j + 2) || (firstMatch && dfs(i + 1, j));
        }

        return firstMatch && dfs(i + 1, j + 1);
    };

    return dfs(0, 0);
};
