var isInterleave = function(s1, s2, s3) {
    if (s1.length + s2.length !== s3.length) return false;

    const dfs = (i, j) => {
        const k = i + j;
        if (k === s3.length) return true;

        if (i < s1.length && s1[i] === s3[k]) {
            if (dfs(i + 1, j)) return true;
        }

        if (j < s2.length && s2[j] === s3[k]) {
            if (dfs(i, j + 1)) return true;
        }

        return false;
    };

    return dfs(0, 0);
};
