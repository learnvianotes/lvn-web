var uniquePaths = function(m, n) {
    const dfs = (r, c) => {
        if (r === m - 1 && c === n - 1) return 1;
        if (r >= m || c >= n) return 0;

        return dfs(r + 1, c) + dfs(r, c + 1);
    };

    return dfs(0, 0);
};
