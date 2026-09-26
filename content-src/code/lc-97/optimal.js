var isInterleave = function(s1, s2, s3) {
    if (s1.length + s2.length !== s3.length) return false;

    const m = s1.length;
    const n = s2.length;

    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(false));
    dp[0][0] = true;

    for (let i = 0; i <= m; i++) {
        for (let j = 0; j <= n; j++) {
            if (i === 0 && j === 0) continue;

            const k = i + j - 1;

            if (i > 0 && dp[i - 1][j] && s1[i - 1] === s3[k]) {
                dp[i][j] = true;
            }

            if (j > 0 && dp[i][j - 1] && s2[j - 1] === s3[k]) {
                dp[i][j] = true;
            }
        }
    }

    return dp[m][n];
};
