var minDistance = function(word1, word2) {
    const dfs = (i, j) => {
        if (i === word1.length) return word2.length - j;
        if (j === word2.length) return word1.length - i;

        if (word1[i] === word2[j]) return dfs(i + 1, j + 1);

        const insert = dfs(i, j + 1);
        const remove = dfs(i + 1, j);
        const replace = dfs(i + 1, j + 1);

        return 1 + Math.min(insert, remove, replace);
    };

    return dfs(0, 0);
};
